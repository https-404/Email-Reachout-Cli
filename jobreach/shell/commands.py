from datetime import datetime, timezone

from jobreach.ai.provider_registry import PROVIDERS, get_provider
from jobreach.app.auth_service import AuthService, connect_gmail
from jobreach.app.campaign_service import CampaignService
from jobreach.app.generation_flow import run_shell_generation
from jobreach.app.provider_setup_service import ProviderSetupService
from jobreach.app.review_service import interactive_review
from jobreach.app.send_service import SendService
from jobreach.config.paths import data_dir, do_not_contact_path, ensure_data_dirs
from jobreach.config.secrets import SecretStore
from jobreach.config.settings import SettingsStore
from jobreach.demo.runner import run_demo_generation
from jobreach.drafts.index import get_batch, list_batches, update_batch_stats
from jobreach.drafts.store import load_drafts, save_drafts
from jobreach.leads.preview import load_leads_with_stats
from jobreach.logs.run_log import record_run
from jobreach.logs.sent_log import SentLog
from jobreach.mail.gmail_auth import get_gmail_email, gmail_connected
from jobreach.mail.gmail_client import GmailClient
from jobreach.safety.do_not_contact import load_do_not_contact
from jobreach.safety.send_guard import can_send_draft
from jobreach.safety.send_scheduler import in_send_window, schedule_times, today_sent_count
from jobreach.shell.menus import run_settings_menu
from jobreach.shell.product_commands import PRODUCT_ALIASES, PRODUCT_COMMANDS, bootstrap_oauth
from jobreach.shell.prompts import (
    choose_number,
    confirm,
    confirm_send,
    confirm_send_high_risk,
    console,
    expand_path,
    prompt_path,
    prompt_text,
)
from jobreach.shell.render import print_batch_table, print_help, print_models_menu, print_status
from jobreach.storage.sqlite_store import SQLiteStore


ALIASES = {
    "setup": "settings",
    "setting": "settings",
    "provider": "change provider",
    "model": "change model",
    "generate": "generate drafts",
    "drafts": "generate drafts",
    "review": "review drafts",
    "send": "send emails",
    "gmail": "auth gmail",
    **PRODUCT_ALIASES,
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
    if normalized.startswith("mark replied "):
        return normalized
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
        tone_preset=settings.tone_preset,
    )
    if batches:
        console.print("[bold]Draft batches[/bold]\n")
        for batch in batches[:10]:
            pending = batch.count - batch.approved - batch.sent
            console.print(
                f"- {batch.id}: Approved {batch.approved}/{batch.count} · Sent {batch.sent} · Pending {max(0, pending)}"
            )
        console.print("")
    campaigns = CampaignService(ctx.settings_store).list_campaigns()
    if campaigns:
        console.print(f"Campaigns: {len(campaigns)}\n")


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

    cv_raw = prompt_path("Enter path to your CV", default=settings.last_cv_path or "")
    if not cv_raw:
        return
    cv_path = expand_path(cv_raw)
    if not cv_path.exists():
        console.print(f"[red]File not found: {cv_path}[/red]")
        return

    leads_raw = prompt_path("Enter path to leads CSV", default=settings.last_leads_path or "")
    if not leads_raw:
        return
    leads_path = expand_path(leads_raw)
    if not leads_path.exists():
        console.print(f"[red]File not found: {leads_path}[/red]")
        return

    leads, stats = load_leads_with_stats(str(leads_path))
    console.print(
        f"\nLeads: {stats.valid} valid ({stats.invalid_skipped} invalid skipped, "
        f"{stats.duplicates_skipped} duplicates removed)\n"
    )

    console.print("How many leads should we process?\n")
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

    process_count = min(len(leads), limit) if limit is not None else len(leads)
    generate_model = settings.generate_model or settings.default_model
    review_model = settings.review_model or settings.default_model
    info = get_provider(settings.default_provider)
    api_calls = process_count * (2 if settings.ai_quality_check and review_model != generate_model else 1)
    console.print(
        f"\nGenerate drafts using:\n"
        f"Provider: {info.display_name}\n"
        f"Model: {generate_model}\n"
        f"Tone: {settings.tone_preset}\n"
        f"Quality check: {'on' if settings.ai_quality_check else 'off'}\n"
        f"Estimated API calls: ~{api_calls}\n"
    )
    if not confirm("Continue?", default=False):
        return

    console.print("\nGenerating drafts...")
    summary = run_shell_generation(
        str(cv_path),
        str(leads_path),
        limit,
        ctx.settings_store,
        ctx.secret_store,
    )

    console.print(f"\n[green]Generated drafts: {summary.generated}[/green]")
    console.print(f"Risk: low {summary.low_risk} · medium {summary.medium_risk} · high {summary.high_risk}")
    if summary.by_recipient_type:
        console.print("By recipient type:")
        for rtype, count in summary.by_recipient_type.items():
            console.print(f"  - {rtype}: {count}")
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
        pending = max(0, batch.count - batch.approved - batch.sent)
        console.print(
            f"{index}. {created} — {batch.count} drafts — Approved {batch.approved} · Sent {batch.sent} · Pending {pending}"
        )
    choice = choose_number("\nChoose batch", len(batches))
    if not choice:
        return
    batch = batches[choice - 1]
    start_index = batch.last_review_index
    if start_index > 0 and start_index < batch.count:
        if confirm(f"Resume from draft {start_index + 1}?", default=True):
            pass
        else:
            start_index = 0
    interactive_review(
        batch.path,
        batch.id,
        profile_path=batch.profile_path,
        settings_store=ctx.settings_store,
        secret_store=ctx.secret_store,
        start_index=start_index,
    )


def _collect_sendable(
    approved: list,
    sent_log: SentLog,
    blocked: set[str],
    allow_high_risk: bool,
) -> tuple[list, list]:
    sendable = []
    high_risk_blocked = []
    for draft in approved:
        already = sent_log.has_been_sent(str(draft.email), draft.subject)
        allowed, reason = can_send_draft(
            draft,
            already,
            blocked,
            require_approved=True,
            allow_high_risk=allow_high_risk,
        )
        if allowed:
            sendable.append(draft)
        elif reason == "high-risk draft":
            high_risk_blocked.append(draft)
    return sendable, high_risk_blocked


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
    crm = SQLiteStore()
    for email in crm.list_replied_emails():
        blocked.add(email.lower())

    sendable, high_risk_blocked = _collect_sendable(approved, sent_log, blocked, allow_high_risk=False)
    include_high_risk = False
    if high_risk_blocked and confirm(f"Include {len(high_risk_blocked)} high-risk draft(s)?", default=False):
        if confirm_send_high_risk():
            sendable.extend(high_risk_blocked)
            include_high_risk = True
        else:
            console.print("High-risk send cancelled.")

    settings = ctx.settings_store.load()
    sent_today = today_sent_count(sent_log.read_all())
    remaining_cap = max(0, settings.daily_send_cap - sent_today)
    if remaining_cap == 0:
        console.print(f"[yellow]Daily send cap ({settings.daily_send_cap}) reached. Try again tomorrow.[/yellow]")
        return

    gmail_email = get_gmail_email() or "your Gmail account"
    preview_rows = [(str(d.email), d.subject[:50], d.risk) for d in sendable[:20]]
    print_batch_table("Send preview", preview_rows, ["Email", "Subject", "Risk"])
    if len(sendable) > 20:
        console.print(f"... and {len(sendable) - 20} more\n")

    console.print(
        f"\nReady to send.\n\n"
        f"From: {gmail_email}\n"
        f"Approved drafts: {len(approved)}\n"
        f"Will send: {len(sendable)} (cap remaining today: {remaining_cap})\n"
        f"Send window: {settings.send_window_start}–{settings.send_window_end} "
        f"({'inside' if in_send_window(settings) else 'outside'} window)\n"
        f"Send delay: {settings.send_delay_seconds} seconds\n"
    )

    console.print("Send mode:\n")
    console.print("1. Send now")
    console.print("2. Dry run (no Gmail API calls)")
    console.print("3. Queue across days")
    console.print("4. Cancel\n")
    mode = choose_number("Choose option", 4)
    if not mode or mode == 4:
        console.print("Cancelled.")
        return

    dry_run = mode == 2
    queue_mode = mode == 3

    console.print("\nHow many should be sent?\n")
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

    to_send = sendable[: min(len(sendable), limit) if limit is not None else len(sendable)]
    to_send = to_send[:remaining_cap]

    if queue_mode:
        days_raw = prompt_text("Spread sends over how many days?", default="2")
        try:
            days = max(1, int(days_raw))
        except ValueError:
            console.print("[red]Invalid number.[/red]")
            return
        times = schedule_times(len(to_send), days, settings)
        for draft, scheduled_at in zip(to_send, times):
            crm.queue_draft(draft.id, batch.path, str(draft.email), scheduled_at)
            draft.status = "queued"
            draft.scheduled_at = scheduled_at
        save_drafts(batch.path, drafts)
        update_batch_stats(batch.id)
        console.print(f"[green]Queued {len(to_send)} draft(s) across {days} day(s).[/green]")
        console.print('Use "send queue run" to process due items.\n')
        return

    label = "Dry run" if dry_run else "Send"
    console.print(
        f"\nJobReach is about to {label.lower()} {len(to_send)} email(s) from {gmail_email}.\n"
        f"Only approved drafts will be included.\n"
    )
    if dry_run:
        if not confirm("Run dry run?", default=True):
            console.print("Cancelled.")
            return
    elif not confirm_send():
        console.print("Send cancelled.")
        return

    creds = AuthService().gmail()
    service = SendService(GmailClient(creds), sent_log)

    def on_sent(draft, message_id):
        crm.record_send_event(draft.id, str(draft.email), draft.subject, message_id, batch.campaign_id)
        record_run("send", {"draft_id": draft.id, "email": str(draft.email), "batch_id": batch.id})

    results = service.send_drafts(
        to_send,
        confirm=True,
        limit=None,
        delay_seconds=settings.send_delay_seconds,
        do_not_contact=blocked,
        require_approved=True,
        dry_run=dry_run,
        allow_high_risk=include_high_risk,
        on_sent=None if dry_run else on_sent,
    )
    if not dry_run:
        save_drafts(batch.path, drafts)
        update_batch_stats(batch.id)
    sent = sum(1 for result in results if result.status == "sent")
    skipped = sum(1 for result in results if result.status == "skipped")
    failed = sum(1 for result in results if result.status == "failed")
    prefix = "Dry run" if dry_run else "Send"
    console.print(f"\n{prefix} complete. Sent: {sent}  Skipped: {skipped}  Failed: {failed}\n")


def handle_send_queue_run(ctx: ShellContext) -> None:
    if not gmail_connected():
        console.print("[yellow]Gmail is not connected. Run: auth gmail[/yellow]")
        return
    settings = ctx.settings_store.load()
    if not in_send_window(settings):
        console.print("[yellow]Outside send window. Adjust settings or try later.[/yellow]")
        return
    crm = SQLiteStore()
    queued = crm.list_queue()
    if not queued:
        console.print("[yellow]Send queue is empty.[/yellow]")
        return
    now = datetime.now(timezone.utc)
    due = [item for item in queued if datetime.fromisoformat(item["scheduled_at"]) <= now]
    if not due:
        console.print("[yellow]No due items in queue yet.[/yellow]")
        return
    limit_raw = prompt_text("How many to process now?", default="10")
    try:
        limit = int(limit_raw)
    except ValueError:
        console.print("[red]Invalid number.[/red]")
        return
    sent_log = SentLog()
    blocked = load_do_not_contact(do_not_contact_path())
    creds = AuthService().gmail()
    service = SendService(GmailClient(creds), sent_log)
    processed = 0
    for item in due[:limit]:
        drafts = load_drafts(item["batch_path"])
        draft = next((d for d in drafts if d.id == item["draft_id"]), None)
        if not draft:
            crm.mark_queue_sent(item["id"])
            continue
        results = service.send_drafts(
            [draft],
            confirm=True,
            limit=1,
            delay_seconds=settings.send_delay_seconds,
            do_not_contact=blocked,
            require_approved=True,
            on_sent=lambda d, mid: crm.record_send_event(d.id, str(d.email), d.subject, mid),
        )
        if results and results[0].status == "sent":
            crm.mark_queue_sent(item["id"])
            save_drafts(item["batch_path"], drafts)
            processed += 1
    console.print(f"[green]Processed {processed} queued send(s).[/green]")


def handle_demo(ctx: ShellContext) -> None:
    console.print("\n[bold]Demo mode[/bold] — sample CV and 5 leads, no API keys required.\n")
    path = run_demo_generation(ctx.settings_store)
    console.print(f"[green]Demo batch created:[/green] {path}")
    console.print('Type "review drafts" to try the review flow.\n')


def handle_mark_replied_command(ctx: ShellContext, command: str) -> None:
    email = command.replace("mark replied", "", 1).strip()
    from jobreach.shell.product_commands import handle_mark_replied

    handle_mark_replied(ctx, email or None)


def handle_auth_gmail(settings_store: SettingsStore | None = None) -> None:
    bootstrap_oauth()
    store = settings_store or SettingsStore()
    connect_gmail(store)


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
    "send queue run": handle_send_queue_run,
    "demo": handle_demo,
    "auth gmail": lambda ctx: handle_auth_gmail(ctx.settings_store),
    "logout gmail": lambda ctx: handle_logout_gmail(ctx.settings_store),
    "debug on": handle_debug_on,
    "debug off": handle_debug_off,
    **PRODUCT_COMMANDS,
}


def dispatch_command(ctx: ShellContext, command: str) -> None:
    if command.startswith("mark replied"):
        handle_mark_replied_command(ctx, command)
        return
    handler = COMMANDS.get(command)
    if handler:
        handler(ctx)
