from rich.console import Console
from rich.panel import Panel

from jobreach.core.models import EmailDraft


def display_drafts(drafts: list[EmailDraft]) -> None:
    console = Console()
    for index, draft in enumerate(drafts, start=1):
        warnings = ", ".join(draft.warnings) if draft.warnings else "None"
        body = (
            f"[{index}] {draft.email}\n"
            f"Company: {draft.company or '-'}\n"
            f"Type: {draft.recipient_type}\n"
            f"Risk: {draft.risk}\n"
            f"Score: {draft.personalization_score}/10\n"
            f"Warnings: {warnings}\n\n"
            f"Subject:\n{draft.subject}\n\n"
            f"Body:\n{draft.body}"
        )
        console.print(Panel(body, title=str(draft.email)))
