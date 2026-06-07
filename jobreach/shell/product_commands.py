from rich.table import Table

from jobreach.ai.tone_presets import TONE_PRESETS, list_tone_preset_ids
from jobreach.app.campaign_service import CampaignService
from jobreach.app.follow_up_service import FollowUpService
from jobreach.config.paths import exports_dir
from jobreach.drafts.exporter import export_campaign_report
from jobreach.drafts.index import get_batch, list_batches
from jobreach.leads.preview import load_leads_with_stats
from jobreach.mail.credentials_bootstrap import ensure_oauth_client_secret
from jobreach.shell.prompts import choose_number, confirm, console, expand_path, prompt_text


def bootstrap_oauth() -> None:
    try:
        ensure_oauth_client_secret()
    except Exception:
        pass


def handle_preview_leads(ctx) -> None:
    settings = ctx.settings_store.load()
    default = settings.last_leads_path or ""
    raw = prompt_text("Enter path to leads CSV", default=default)
    if not raw:
        return
    path = expand_path(raw)
    leads, stats = load_leads_with_stats(str(path))
    console.print(f"\nValid leads: {stats.valid}")
    console.print(f"Invalid skipped: {stats.invalid_skipped}")
    console.print(f"Duplicates skipped: {stats.duplicates_skipped}\n")
    table = Table(title="Leads preview")
    for col in ("email", "company", "recipient_type", "role"):
        table.add_column(col)
    for lead in leads[:15]:
        table.add_row(str(lead.email), lead.company or "", lead.recipient_type or "", lead.role or "")
    console.print(table)


def handle_change_tone(ctx) -> None:
    console.print("\nTone presets:\n")
    ids = list_tone_preset_ids()
    for index, preset_id in enumerate(ids, start=1):
        console.print(f"{index}. {TONE_PRESETS[preset_id]['label']} ({preset_id})")
    choice = choose_number("Choose tone", len(ids))
    if not choice:
        return
    preset_id = ids[choice - 1]
    ctx.settings_store.update(tone_preset=preset_id)
    console.print(f"[green]Tone preset set to {preset_id}.[/green]")


def handle_campaigns(ctx) -> None:
    service = CampaignService(ctx.settings_store)
    campaigns = service.list_campaigns()
    if not campaigns:
        console.print("[yellow]No campaigns yet. Use: new campaign[/yellow]")
        return
    for campaign in campaigns:
        console.print(
            f"- {campaign['name']} ({campaign['id'][:8]}...) "
            f"created {campaign['created_at'][:10]}"
        )


def handle_new_campaign(ctx) -> None:
    name = prompt_text("Campaign name")
    if not name:
        return
    settings = ctx.settings_store.load()
    cv = prompt_text("CV path (optional)", default=settings.last_cv_path or "")
    leads = prompt_text("Leads path (optional)", default=settings.last_leads_path or "")
    service = CampaignService(ctx.settings_store)
    cid = service.create_campaign(name, cv or None, leads or None)
    console.print(f"[green]Campaign created: {name} ({cid})[/green]")


def handle_mark_replied(ctx, email: str | None = None) -> None:
    if not email:
        email = prompt_text("Email address")
    if not email:
        return
    add_dnc = confirm("Add to do-not-contact list?", default=False)
    CampaignService(ctx.settings_store).mark_replied(email, add_to_dnc=add_dnc)
    console.print(f"[green]Marked {email} as replied.[/green]")


def handle_dnc_list(ctx) -> None:
    entries = CampaignService(ctx.settings_store).list_dnc()
    if not entries:
        console.print("Do-not-contact list is empty.")
        return
    for entry in entries:
        console.print(f"- {entry}")


def handle_dnc_add(ctx) -> None:
    email = prompt_text("Email to block")
    if email:
        CampaignService(ctx.settings_store).add_dnc(email)
        console.print("[green]Added to do-not-contact.[/green]")


def handle_dnc_remove(ctx) -> None:
    email = prompt_text("Email to unblock")
    if email and CampaignService(ctx.settings_store).remove_dnc(email):
        console.print("[green]Removed from do-not-contact.[/green]")
    else:
        console.print("[yellow]Not found.[/yellow]")


def handle_follow_up(ctx) -> None:
    service = FollowUpService(ctx.settings_store, ctx.secret_store)
    path = service.create_follow_up_batch()
    if path:
        console.print(f"[green]Follow-up batch created:[/green] {path}")
    else:
        console.print("[yellow]No follow-up candidates found.[/yellow]")


def handle_export_campaign(ctx) -> None:
    name = prompt_text("Report name", default="campaign")
    path = export_campaign_report(name, exports_dir())
    console.print(f"[green]Report saved:[/green] {path}")


def handle_send_queue_status(ctx) -> None:
    from jobreach.storage.sqlite_store import SQLiteStore

    queued = SQLiteStore().list_queue()
    console.print(f"Queued sends: {len(queued)}")
    for item in queued[:20]:
        console.print(f"- {item['email']} at {item['scheduled_at']}")


PRODUCT_ALIASES = {
    "preview leads": "preview leads",
    "leads": "preview leads",
    "change tone": "change tone",
    "tone": "change tone",
    "campaigns": "campaigns",
    "new campaign": "new campaign",
    "follow up": "follow up",
    "followup": "follow up",
    "dnc list": "dnc list",
    "dnc add": "dnc add",
    "dnc remove": "dnc remove",
    "export campaign": "export campaign",
    "send queue status": "send queue status",
}

PRODUCT_COMMANDS = {
    "preview leads": handle_preview_leads,
    "change tone": handle_change_tone,
    "campaigns": handle_campaigns,
    "new campaign": handle_new_campaign,
    "follow up": handle_follow_up,
    "dnc list": handle_dnc_list,
    "dnc add": handle_dnc_add,
    "dnc remove": handle_dnc_remove,
    "export campaign": handle_export_campaign,
    "send queue status": handle_send_queue_status,
}
