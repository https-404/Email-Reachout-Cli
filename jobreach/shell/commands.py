from jobreach.ai.provider_registry import PROVIDERS, get_provider
from jobreach.app.auth_service import AuthService
from jobreach.app.generation_flow import run_shell_generation
from jobreach.app.provider_setup_service import ProviderSetupService
from jobreach.app.review_service import interactive_review
from jobreach.app.send_service import SendService
from jobreach.config.paths import data_dir, do_not_contact_path, ensure_data_dirs
from jobreach.config.secrets import SecretStore
from jobreach.config.settings import SettingsStore
from jobreach.drafts.index import list_batches, update_batch_stats
from jobreach.drafts.store import load_drafts, save_drafts
from jobreach.logs.sent_log import SentLog
from jobreach.mail.gmail_auth import get_gmail_email, gmail_connected
from jobreach.mail.gmail_client import GmailClient
from jobreach.safety.do_not_contact import load_do_not_contact
from jobreach.safety.send_guard import can_send_draft
from jobreach.shell.menus import run_settings_menu
from jobreach.shell.prompts import choose_number, confirm, confirm_send, console, expand_path, prompt_text
from jobreach.shell.render import print_help, print_models_menu, print_status


ALIASES = {
    "setup": "settings",
    "provider": "change provider",
    "model": "change model",
    "generate": "generate drafts",
    "drafts": "generate drafts",
    "review": "review drafts",
    "send": "send emails",
    "gmail": "auth gmail",
}


class ShellContext:
    def __init__(self):
        ensure_data_dirs()
        self.settings_store = SettingsStore()
        self.secret_store = SecretStore()
        self.provider_setup = ProviderSetupService(self.settings_store, self.secret_store)
        self.debug = False


def resolve_command(command: str) -> str:
    normalized = " ".join(command.strip().lower().split())
    return ALIASES.get(normalized, normalized)


def handle_help(_ctx: ShellContext) -> None:
    print_help()


def handle_status(ctx: ShellContext) -> None:
    settings = ctx.settings_store.load()
    provider = settings.default_provider
    model = settings.default_model or "-"
    if provider:
        provider_label = get_provider(provider).display_name
        api_key_status = "saved locally" if ctx.secret_store.has_provider_key(provider) else "missing"
    else:
        provider_label = "Not configured"
        api_key_status = "missing"

    gmail_email = get_gmail_email()
    if gmail_email:
        gmail_status = f"connected as {gmail_email}"
    elif gmail_connected():
        gmail_status = "connected"
    else:
        gmail_status = "not connected"

    batches = list_batches()
    drafts_count = sum(batch.count for batch in batches)
    sent_count = SentLog().count_sent()
    dnc_count = len(load_do_not_contact(do_not_contact_path()))

    print_status(
        provider=provider_label,
        model=model,
        api_key_status=api_key_status,
        gmail_status=gmail_status,
        data_dir=str(data_dir()),
        drafts_count=drafts_count,
        sent_count=sent_count,
        dnc_count=dnc_count,
    )


def handle_settings(ctx: ShellContext) -> None:
    run_settings_menu(ctx.settings_store, ctx.secret_store, ctx.provider_setup)


def handle_models(ctx: ShellContext) -> None:
    settings = ctx.settings_store.load()
    if not settings.default_provider:
        console.print("[yellow]No provider configured. Use: change provider[/yellow]")
        return
    info = get_provider(settings.default_provider)
    print_models_menu(info.display_name, settings.default_model or "-")
    if ctx.secret_store.has_provider_key(settings.default_provider):
        if confirm("Would you like to refresh available models?", default=False):
            models = ctx.provider_setup.list_models_for_current(refresh=True)
            console.print(f"Fetched {len(models)} model(s).")


def handle_change_provider(ctx: ShellContext) -> None:
    ctx.provider_setup.setup_provider(allow_back=True)


def handle_change_model(ctx: ShellContext) -> None:
    ctx.provider_setup.change_model()


def handle_generate_drafts(ctx: ShellContext) -> None:
    settings = ctx.settings_store.load()
    if not settings.default_provider or not settings.default_model:
        console.print("[yellow]Configure AI provider first: settings[/yellow]")
        return
    if not ctx.secret_store.has_provider_key(settings.default_provider):
        console.print("[yellow]Missing API key. Run: settings[/yellow]")
        return

    cv_raw = prompt_text("Enter path to your CV")
    if not cv_raw:
        return
    cv_path = expand_path(cv_raw)
    if not cv_path.exists():
        console.print(f"[red]File not found: {cv_path}[/red]")
        return

    leads_raw = prompt_text("Enter path to leads CSV")
    if not leads_raw:
        return
    leads_path = expand_path(leads_raw)
    if not leads_path.exists():
        console.print(f"[red]File not found: {leads_path}[/red]")
        return

    console.print("\nHow many leads should we process?\n")
    console.print("1. All")
    console.print("2. First 10")
    console.print("3. First 25")
    console.print("4. Custom number\n")
    limit_choice = choose_number("Choose option", 4)
    limit = None
    if limit_choice == 2:
        limit = 10
    elif limit_choice == 3:
        limit = 25
    elif limit_choice == 4:
        raw = prompt_text("Custom number")
        try:
            limit = int(raw)
        except ValueError:
            console.print("[red]Invalid number.[/red]")
            return

    info = get_provider(settings.default_provider)
    console.print(
        f"\nGenerate drafts using:\n"
        f"Provider: {info.display_name}\n"
        f"Model: {settings.default_model}\n"
    )
    if not confirm("Continue?", default=False):
        return

    console.print("\nGenerating drafts...")
    try:
        summary = run_shell_generation(
            str(cv_path),
            str(leads_path),
            limit,
            ctx.settings_store,
            ctx.secret_store,
        )
    except Exception as exc:
        raise exc

    console.print(f"\n[green]Generated drafts: {summary.generated}[/green]")
    console.print(f"High-risk drafts: {summary.high_risk}")
    if summary.failed:
        console.print(f"Failed drafts: {summary.failed}")
    console.print(f"\nDrafts saved to:\n{summary.output_path}")
    console.print('Type "review drafts" to review them.\n')


def handle_review_drafts(ctx: ShellContext) -> None:
    batches = list_batches()
    if not batches:
        console.print("[yellow]No draft batches found. Run: generate drafts[/yellow]")
        return

    console.print("\nDraft batches:\n")
    for index, batch in enumerate(batches, start=1):
        created = batch.created_at.replace("T", " ").split(".")[0].replace("Z", "")
        console.print(
            f"{index}. {created} — {batch.count} drafts — {batch.provider}/{batch.model}"
        )
    choice = choose_number("\nChoose batch", len(batches))
    if not choice:
        return
    batch = batches[choice - 1]
    interactive_review(batch.path, batch.id)


def handle_send_emails(ctx: ShellContext) -> None:
    if not gmail_connected():
        console.print("[yellow]Gmail is not connected. Run: auth gmail[/yellow]")
        return

    batches = [batch for batch in list_batches() if batch.approved > 0]
    if not batches:
        console.print("[yellow]No batches with approved drafts. Run: review drafts[/yellow]")
        return

    console.print("\nChoose draft batch to send:\n")
    for index, batch in enumerate(batches, start=1):
        created = batch.created_at.replace("T", " ").split(".")[0].replace("Z", "")
        console.print(f"{index}. {created} — {batch.approved} approved — {batch.sent} sent")
    choice = choose_number("Choose batch", len(batches))
    if not choice:
        return
    batch = batches[choice - 1]
    drafts = load_drafts(batch.path)
    approved = [draft for draft in drafts if draft.status == "approved"]

    sent_log = SentLog()
    blocked = load_do_not_contact(do_not_contact_path())
    high_risk = sum(1 for draft in approved if draft.risk == "high")
    already_sent = sum(
        1
        for draft in approved
        if sent_log.has_been_sent(str(draft.email), draft.subject) or draft.status == "sent"
    )
    dnc = sum(1 for draft in approved if str(draft.email).lower() in blocked)
    sendable = [
        draft
        for draft in approved
        if can_send_draft(
            draft,
            sent_log.has_been_sent(str(draft.email), draft.subject),
            blocked,
            require_approved=True,
        )[0]
    ]

    gmail_email = get_gmail_email() or "your Gmail account"
    console.print(
        f"\nReady to send.\n\n"
        f"From: {gmail_email}\n"
        f"Approved drafts: {len(approved)}\n"
        f"Will send: {len(sendable)}\n"
        f"Skipped:\n"
        f"- High risk: {high_risk}\n"
        f"- Already sent: {already_sent}\n"
        f"- Do not contact: {dnc}\n"
    )
    settings = ctx.settings_store.load()
    console.print(f"Send delay: {settings.send_delay_seconds} seconds\n")
    console.print("How many should be sent?\n")
    console.print("1. All")
    console.print("2. First 10")
    console.print("3. Custom")
    console.print("4. Cancel\n")
    limit_choice = choose_number("Choose option", 4)
    if not limit_choice or limit_choice == 4:
        console.print("Cancelled.")
        return
    limit = None
    if limit_choice == 2:
        limit = 10
    elif limit_choice == 3:
        raw = prompt_text("Custom number")
        try:
            limit = int(raw)
        except ValueError:
            console.print("[red]Invalid number.[/red]")
            return

    to_send = min(len(sendable), limit) if limit is not None else len(sendable)
    console.print(
        f"\nJobReach is about to send real emails from your connected Gmail account.\n"
        f"Only approved drafts will be sent.\n"
        f"You are about to send {to_send} real email(s) from {gmail_email}.\n"
    )
    if not confirm_send():
        console.print("Send cancelled.")
        return

    creds = AuthService().gmail()
    service = SendService(GmailClient(creds), sent_log)
    results = service.send_drafts(
        drafts,
        confirm=True,
        limit=limit,
        delay_seconds=settings.send_delay_seconds,
        do_not_contact=blocked,
        require_approved=True,
    )
    save_drafts(batch.path, drafts)
    update_batch_stats(batch.id)
    sent = sum(1 for result in results if result.status == "sent")
    skipped = sum(1 for result in results if result.status == "skipped")
    failed = sum(1 for result in results if result.status == "failed")
    console.print(f"\nSent: {sent}  Skipped: {skipped}  Failed: {failed}\n")


def handle_auth_gmail(settings_store: SettingsStore | None = None) -> None:
    store = settings_store or SettingsStore()
    console.print(
        "\nJobReach uses Gmail OAuth to send from your account.\n"
        "It does not ask for your Gmail password.\n"
        f"It stores a local OAuth token at {data_dir() / 'tokens' / 'gmail_token.json'}.\n"
    )
    if not confirm("Continue?", default=False):
        return
    console.print("\nOpening browser for Google sign-in...")
    AuthService().gmail()
    store.update(gmail_connected_hint=True)
    email = get_gmail_email()
    console.print("[green]Gmail connected successfully.[/green]")
    if email:
        console.print(f"Signed in as: {email}")


def handle_logout_gmail(settings_store: SettingsStore | None = None) -> None:
    store = settings_store or SettingsStore()
    removed = AuthService().logout()
    store.update(gmail_connected_hint=False)
    console.print("Gmail disconnected." if removed else "No Gmail token found.")


def handle_debug_on(ctx: ShellContext) -> None:
    ctx.debug = True
    console.print("[green]Debug mode enabled.[/green]")


def handle_debug_off(ctx: ShellContext) -> None:
    ctx.debug = False
    console.print("[green]Debug mode disabled.[/green]")


COMMANDS = {
    "help": handle_help,
    "status": handle_status,
    "settings": handle_settings,
    "models": handle_models,
    "change provider": handle_change_provider,
    "change model": handle_change_model,
    "generate drafts": handle_generate_drafts,
    "review drafts": handle_review_drafts,
    "send emails": handle_send_emails,
    "auth gmail": lambda ctx: handle_auth_gmail(ctx.settings_store),
    "logout gmail": lambda ctx: handle_logout_gmail(ctx.settings_store),
    "debug on": handle_debug_on,
    "debug off": handle_debug_off,
}
