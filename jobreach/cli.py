import sys
import traceback
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from jobreach.ai.factory import AIClientFactory
from jobreach.app.auth_service import AuthService
from jobreach.app.generation_service import GenerationService
from jobreach.app.profile_service import ProfileService, save_profile
from jobreach.app.profile_service import load_profile
from jobreach.app.review_service import interactive_review, review_drafts
from jobreach.app.send_service import SendService
from jobreach.config.paths import data_dir, do_not_contact_path, ensure_data_dirs, gmail_token_path
from jobreach.config.settings import get_default_delay_seconds, get_default_model, get_default_provider, provider_env_status
from jobreach.core.errors import JobReachError
from jobreach.drafts.store import load_drafts, save_drafts
from jobreach.leads.loader import load_leads_csv
from jobreach.logs.sent_log import SentLog
from jobreach.mail.gmail_auth import authenticate_gmail, gmail_connected
from jobreach.mail.gmail_client import GmailClient
from jobreach.safety.do_not_contact import load_do_not_contact
from jobreach.workflows.simple_pipeline import run_generation_pipeline

console = Console()
app = typer.Typer(no_args_is_help=True)
auth_app = typer.Typer(no_args_is_help=True)
app.add_typer(auth_app, name="auth")


def _handle_error(exc: Exception, debug: bool = False) -> None:
    if debug:
        traceback.print_exception(type(exc), exc, exc.__traceback__)
    else:
        console.print(f"[red]Error:[/red] {exc}")
    raise typer.Exit(1)


def _prompt_optional_int(label: str, default: int | None = None) -> int | None:
    default_text = "" if default is None else str(default)
    raw = typer.prompt(label, default=default_text, show_default=default is not None).strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise JobReachError(f"{label} must be a number") from exc


def _prompt_float(label: str, default: float) -> float:
    raw = typer.prompt(label, default=str(default)).strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise JobReachError(f"{label} must be a number") from exc


def _send_loaded_drafts(
    draft_rows,
    drafts_path: str,
    limit: int | None,
    delay_seconds: int,
    do_not_contact_file: str | None,
    force: bool,
    require_approved: bool = False,
):
    if not gmail_token_path().exists():
        raise JobReachError("Gmail is not connected. Run: jobreach auth gmail")
    creds = authenticate_gmail()
    blocked_path = do_not_contact_file or str(do_not_contact_path())
    blocked = load_do_not_contact(blocked_path)
    service = SendService(GmailClient(creds), SentLog())
    results = service.send_drafts(
        draft_rows,
        True,
        limit,
        delay_seconds,
        blocked,
        force,
        require_approved=require_approved,
    )
    save_drafts(drafts_path, draft_rows)
    sent = sum(1 for result in results if result.status == "sent")
    skipped = sum(1 for result in results if result.status == "skipped")
    failed = sum(1 for result in results if result.status == "failed")
    console.print(f"Sent: {sent}  Skipped: {skipped}  Failed: {failed}")


@auth_app.command("gmail")
def auth_gmail(debug: bool = typer.Option(False, "--debug")):
    try:
        ensure_data_dirs()
        AuthService().gmail()
        console.print("[green]Gmail connected.[/green]")
    except Exception as exc:
        _handle_error(exc, debug)


@auth_app.command("status")
def auth_status():
    table = Table(title="JobReach Auth Status")
    table.add_column("Service")
    table.add_column("Status")
    table.add_row("Gmail", "connected" if gmail_connected() else "not connected")
    for provider, configured in provider_env_status().items():
        table.add_row(provider, "configured" if configured else "missing")
    console.print(table)


@auth_app.command("logout")
def auth_logout():
    removed = AuthService().logout()
    console.print("Gmail token deleted." if removed else "No Gmail token found.")


@app.command("models")
def models():
    console.print("Available providers:\n")
    console.print("gemini\n  env: GEMINI_API_KEY\n  example model: gemini-1.5-flash\n")
    console.print("openai\n  env: OPENAI_API_KEY\n  example model: gpt-4o-mini\n")
    console.print("anthropic\n  env: ANTHROPIC_API_KEY\n  example model: claude-3-5-haiku-latest")


@app.command("start")
def start(debug: bool = typer.Option(False, "--debug")):
    try:
        ensure_data_dirs()
        console.print("[bold]JobReach guided setup[/bold]")
        console.print("This will collect inputs, generate drafts, show them for review, then ask before sending.\n")

        if not gmail_connected() and typer.confirm("Gmail is not connected. Connect Gmail now?", default=False):
            AuthService().gmail()
            console.print("[green]Gmail connected.[/green]")

        provider = typer.prompt("AI provider", default=get_default_provider()).strip()
        model = typer.prompt("AI model", default=get_default_model()).strip()
        temperature = _prompt_float("Temperature", 0.4)
        ai_quality_check = typer.confirm("Run optional AI quality review? This may cost extra API calls.", default=False)

        source_kind = typer.prompt("Use a CV file or existing profile JSON? Enter cv/profile", default="cv").strip().lower()
        if source_kind not in {"cv", "profile"}:
            raise JobReachError("Choose either cv or profile")

        ai_client = AIClientFactory.create(provider, model, temperature)
        if source_kind == "profile":
            profile_path = typer.prompt("Profile JSON path").strip()
            candidate = load_profile(profile_path)
        else:
            cv_path = typer.prompt("CV path (.txt, .pdf, .docx)").strip()
            candidate = ProfileService(ai_client).create_profile_from_cv(cv_path)
            if typer.confirm("Save extracted profile JSON?", default=True):
                default_profile_path = str(data_dir() / "cache" / "profiles" / "profile.json")
                profile_out = typer.prompt("Profile output path", default=default_profile_path).strip()
                save_profile(candidate, profile_out)
                console.print(f"[green]Profile saved:[/green] {profile_out}")

        leads_path = typer.prompt("Leads CSV path").strip()
        default_drafts_path = str(data_dir() / "cache" / "generations" / "drafts.csv")
        drafts_path = typer.prompt("Drafts output CSV path", default=default_drafts_path).strip()
        max_leads = _prompt_optional_int("Maximum leads to generate now (blank for all)")

        leads = load_leads_csv(leads_path)
        if max_leads is not None:
            leads = leads[:max_leads]
        if not leads:
            raise JobReachError("No valid leads found")

        console.print(f"\nGenerating drafts for {len(leads)} lead(s)...")
        drafts = GenerationService(ai_client).generate_drafts(candidate, leads, ai_quality_check=ai_quality_check)
        save_drafts(drafts_path, drafts)
        console.print(f"[green]Drafts saved:[/green] {drafts_path}\n")

        review_drafts(drafts)

        if not typer.confirm("Send reviewed non-high-risk drafts now?", default=False):
            console.print(f"Done. Review or send later with: jobreach review --drafts {drafts_path}")
            return

        if not gmail_connected():
            if typer.confirm("Gmail is still not connected. Connect Gmail now?", default=True):
                AuthService().gmail()
            else:
                raise JobReachError("Gmail is not connected. Run: jobreach auth gmail")

        limit = _prompt_optional_int("Send limit (blank for all)", default=min(10, len(drafts)))
        delay_seconds = _prompt_optional_int("Delay seconds between sends", default=get_default_delay_seconds())
        do_not_contact_file = typer.prompt("Do-not-contact CSV path (blank for default)", default="", show_default=False).strip() or None
        force = typer.confirm("Force duplicate/sent-status sends? High-risk drafts still stay blocked.", default=False)

        if not typer.confirm("Final confirmation: send emails now?", default=False):
            console.print(f"Send cancelled. Drafts remain saved at: {drafts_path}")
            return

        _send_loaded_drafts(drafts, drafts_path, limit, delay_seconds or 0, do_not_contact_file, force)
    except Exception as exc:
        _handle_error(exc, debug)


@app.command("profile")
def profile(
    cv: str = typer.Option(..., "--cv"),
    out: str = typer.Option(..., "--out"),
    provider: str = typer.Option(get_default_provider(), "--provider"),
    model: str = typer.Option(get_default_model(), "--model"),
    temperature: float = typer.Option(0.4, "--temperature"),
    debug: bool = typer.Option(False, "--debug"),
):
    try:
        ai_client = AIClientFactory.create(provider, model, temperature)
        candidate = ProfileService(ai_client).create_profile_from_cv(cv)
        save_profile(candidate, out)
        console.print(f"[green]Profile saved:[/green] {out}")
    except Exception as exc:
        _handle_error(exc, debug)


@app.command("generate")
def generate(
    cv: Optional[str] = typer.Option(None, "--cv"),
    profile_path: Optional[str] = typer.Option(None, "--profile"),
    leads: str = typer.Option(..., "--leads"),
    out: str = typer.Option(..., "--out"),
    provider: str = typer.Option(get_default_provider(), "--provider"),
    model: str = typer.Option(get_default_model(), "--model"),
    temperature: float = typer.Option(0.4, "--temperature"),
    ai_quality_check: bool = typer.Option(False, "--ai-quality-check"),
    max_leads: Optional[int] = typer.Option(None, "--max-leads"),
    debug: bool = typer.Option(False, "--debug"),
):
    try:
        if not cv and not profile_path:
            raise JobReachError("Either --cv or --profile is required")
        ai_client = AIClientFactory.create(provider, model, temperature)
        drafts = run_generation_pipeline(cv, profile_path, leads, out, ai_client, ai_quality_check, max_leads)
        console.print(f"[green]Drafts saved:[/green] {out} ({len(drafts)} drafts)")
    except Exception as exc:
        _handle_error(exc, debug)


@app.command("review")
def review(drafts: str = typer.Option(..., "--drafts"), debug: bool = typer.Option(False, "--debug")):
    try:
        if sys.stdin.isatty() and sys.stdout.isatty():
            from jobreach.drafts.index import list_batches

            batches = [b for b in list_batches() if b.path == drafts or drafts.endswith(b.id)]
            batch = batches[0] if batches else None
            interactive_review(
                drafts,
                batch.id if batch else "cli",
                profile_path=batch.profile_path if batch else None,
            )
        else:
            review_drafts(load_drafts(drafts))
    except Exception as exc:
        _handle_error(exc, debug)


@app.command("send")
def send(
    drafts: str = typer.Option(..., "--drafts"),
    confirm: bool = typer.Option(False, "--confirm"),
    limit: Optional[int] = typer.Option(None, "--limit"),
    delay_seconds: int = typer.Option(get_default_delay_seconds(), "--delay-seconds"),
    force: bool = typer.Option(False, "--force"),
    approved_only: bool = typer.Option(False, "--approved-only"),
    do_not_contact: Optional[str] = typer.Option(None, "--do-not-contact"),
    debug: bool = typer.Option(False, "--debug"),
):
    try:
        draft_rows = load_drafts(drafts)
        if not confirm:
            console.print("[yellow]Refusing to send without --confirm.[/yellow]")
            return
        _send_loaded_drafts(
            draft_rows,
            drafts,
            limit,
            delay_seconds,
            do_not_contact,
            force,
            require_approved=approved_only,
        )
    except Exception as exc:
        _handle_error(exc, debug)


@app.command("leads-preview")
def leads_preview(leads: str = typer.Option(..., "--leads"), limit: int = typer.Option(10, "--limit")):
    loaded = load_leads_csv(leads)
    table = Table(title=f"Leads Preview ({len(loaded)} valid)")
    for column in ("email", "company", "recipient_type", "role"):
        table.add_column(column)
    for lead in loaded[:limit]:
        table.add_row(str(lead.email), lead.company or "", lead.recipient_type or "", lead.role or "")
    console.print(table)


@app.command("demo")
def demo(debug: bool = typer.Option(False, "--debug")):
    try:
        from jobreach.demo.runner import run_demo_generation

        path = run_demo_generation()
        console.print(f"[green]Demo batch created:[/green] {path}")
    except Exception as exc:
        _handle_error(exc, debug)


def main():
    if len(sys.argv) == 1:
        from jobreach.shell.app import JobReachShell

        JobReachShell().run()
    else:
        app()


if __name__ == "__main__":
    main()
