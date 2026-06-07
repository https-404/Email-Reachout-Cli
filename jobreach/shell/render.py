from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from jobreach.core.models import EmailDraft

console = Console()


def print_help() -> None:
    console.print(
        """
Available commands:

status              Show current configuration and local stats
settings            Open settings menu
models              Show current provider and model
change provider     Change AI provider and API key
change model        Change model for current provider
change tone         Set email tone preset
preview leads       Preview and validate a leads CSV
generate drafts     Generate outreach drafts from CV and leads
review drafts       Review, edit, and approve drafts
send emails         Send approved drafts (dry-run / queue supported)
send queue status   Show queued sends
send queue run      Process due queued sends
campaigns           List campaigns
new campaign        Create a campaign
follow up           Generate follow-up batch for no-reply contacts
mark replied <email> Mark a contact as replied
dnc list / add / remove  Manage do-not-contact list
export campaign     Export HTML/Markdown campaign report
demo                Try JobReach with sample data (no API keys)
auth gmail          Connect Gmail
logout gmail        Disconnect Gmail
debug on            Show stack traces on errors
debug off           Hide stack traces on errors
exit                Close JobReach
"""
    )


def print_startup_banner(
    provider_label: str,
    model_label: str,
    gmail_label: str,
    draft_batches: int,
    sent_count: int,
    configured: bool,
) -> None:
    console.print("\n[bold]JobReach[/bold]\n")
    if configured:
        console.print(f"AI: {provider_label} / {model_label}")
        console.print(f"Gmail: {gmail_label}")
        console.print(f"Draft batches: {draft_batches}")
        console.print(f"Sent emails: {sent_count}")
    else:
        console.print("AI: Not configured")
        console.print(f"Gmail: {gmail_label}")
        console.print('\nType "settings" to configure JobReach.')
    console.print('\nType "help" for commands.\n')


def print_status(
    provider: str,
    model: str,
    api_key_status: str,
    gmail_status: str,
    data_dir: str,
    drafts_count: int,
    sent_count: int,
    dnc_count: int,
    tone_preset: str = "default",
) -> None:
    console.print("\n[bold]JobReach Status[/bold]\n")
    console.print(f"AI Provider: {provider}")
    console.print(f"AI Model: {model}")
    console.print(f"Tone preset: {tone_preset}")
    console.print(f"API Key: {api_key_status}")
    console.print(f"Gmail: {gmail_status}")
    console.print(f"Data Directory: {data_dir}")
    console.print(f"Drafts: {drafts_count}")
    console.print(f"Sent Emails: {sent_count}")
    console.print(f"Do Not Contact: {dnc_count}\n")


def print_draft(draft: EmailDraft, index: int, total: int) -> None:
    warnings = ", ".join(draft.warnings) if draft.warnings else "None"
    body = (
        f"Draft {index} of {total}\n\n"
        f"To: {draft.email}\n"
        f"Company: {draft.company or '-'}\n"
        f"Type: {draft.recipient_type}\n"
        f"Risk: {draft.risk}\n"
        f"Score: {draft.personalization_score}/10\n"
        f"Warnings: {warnings}\n\n"
        f"Subject:\n{draft.subject}\n\n"
        f"Body:\n{draft.body}"
    )
    console.print(Panel(body, title=f"Draft {index}/{total}"))


def print_batch_table(title: str, rows: list[tuple[str, ...]], columns: list[str]) -> None:
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def print_models_menu(provider_name: str, model: str) -> None:
    console.print(f"\nCurrent AI provider: {provider_name}")
    console.print(f"Current model: {model}\n")
    console.print("Available providers:\n")
    console.print("1. OpenAI")
    console.print("2. Google Gemini")
    console.print("3. Anthropic Claude\n")
