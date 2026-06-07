import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone

from jobreach.ai.factory import AIClientFactory
from jobreach.app.generation_service import GenerationService
from jobreach.app.profile_service import load_profile
from jobreach.config.settings import SettingsStore
from jobreach.core.models import CandidateProfile, EmailDraft, Lead
from jobreach.drafts.index import update_batch_review_index, update_batch_stats
from jobreach.drafts.reviewer import display_drafts
from jobreach.drafts.store import load_drafts, save_drafts
from jobreach.shell.prompts import choose_menu_option, confirm, console, prompt_text
from jobreach.shell.render import print_draft
from jobreach.utils.time import utc_now_iso


@dataclass
class ReviewSummary:
    approved: int = 0
    skipped: int = 0
    reviewed: int = 0


REVIEW_ALIASES = {
    "1": 1, "approve": 1,
    "2": 2, "skip": 2,
    "3": 3, "edit subject": 3, "subject": 3,
    "4": 4, "edit body": 4, "body": 4,
    "5": 5, "regenerate": 5, "regen": 5,
    "6": 6, "alt subject": 6, "alternate": 6,
    "7": 7, "next": 7,
    "8": 8, "stop": 8, "back": 8, "quit": 8,
}


def review_drafts(drafts: list[EmailDraft]) -> None:
    display_drafts(drafts)


def _edit_body_multiline() -> str:
    editor = os.environ.get("EDITOR", "nano")
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write("# Edit draft body. Save and close the editor.\n")
        tmp_path = tmp.name
    subprocess.call([editor, tmp_path])
    text = open(tmp_path, encoding="utf-8").read()  # noqa: SIM115
    os.unlink(tmp_path)
    lines = [line for line in text.splitlines() if not line.startswith("# Edit draft")]
    return "\n".join(lines).strip()


def interactive_review(
    batch_path: str,
    batch_id: str,
    profile_path: str | None = None,
    settings_store: SettingsStore | None = None,
    secret_store=None,
    start_index: int = 0,
) -> ReviewSummary:
    drafts = load_drafts(batch_path)
    summary = ReviewSummary()
    index = start_index
    total = len(drafts)
    settings_store = settings_store or SettingsStore()
    settings = settings_store.load()
    profile: CandidateProfile | None = None
    if profile_path:
        profile = load_profile(profile_path)

    hint = "Actions: approve, skip, edit subject/body, regenerate, alt subject, next, stop"
    while index < total:
        draft = drafts[index]
        print_draft(draft, index + 1, total)
        if draft.quality_reason:
            console.print(f"[dim]Quality: {draft.quality_reason}[/dim]")
        console.print(
            "\n1. Approve  2. Skip  3. Edit subject  4. Edit body\n"
            "5. Regenerate  6. Use alt subject  7. Next  8. Stop\n"
        )
        choice = choose_menu_option("Choose action", 8, REVIEW_ALIASES, hint)
        if choice is None or choice == 8:
            break
        if choice == 1:
            draft.status = "approved"
            summary.approved += 1
            summary.reviewed += 1
            save_drafts(batch_path, drafts)
            index += 1
        elif choice == 2:
            draft.status = "skipped"
            summary.skipped += 1
            summary.reviewed += 1
            save_drafts(batch_path, drafts)
            index += 1
        elif choice == 3:
            draft.subject = prompt_text("New subject", default=draft.subject)
            draft.edited_at = utc_now_iso()
            save_drafts(batch_path, drafts)
        elif choice == 4:
            draft.body = _edit_body_multiline() or draft.body
            draft.edited_at = utc_now_iso()
            save_drafts(batch_path, drafts)
        elif choice == 5:
            if profile and secret_store:
                lead = Lead(email=str(draft.email), company=draft.company, recipient_type=draft.recipient_type)
                ai = AIClientFactory.from_settings(settings, secret_store)
                regen = GenerationService(ai).regenerate_draft(
                    profile, lead, tone_preset=settings.tone_preset, ai_quality_check=settings.ai_quality_check
                )
                draft.subject = regen.subject
                draft.body = regen.body
                draft.alt_subject = regen.alt_subject
                draft.risk = regen.risk
                draft.warnings = regen.warnings
                draft.quality_reason = regen.quality_reason
                draft.edited_at = utc_now_iso()
                save_drafts(batch_path, drafts)
            else:
                console.print("[yellow]Profile not available for regeneration.[/yellow]")
        elif choice == 6:
            if draft.alt_subject:
                draft.subject, draft.alt_subject = draft.alt_subject, draft.subject
                draft.edited_at = utc_now_iso()
                save_drafts(batch_path, drafts)
            else:
                console.print("[yellow]No alternate subject available.[/yellow]")
        elif choice == 7:
            index += 1

        update_batch_review_index(batch_id, index)

    update_batch_stats(batch_id)
    console.print(
        f"\nReview complete. Approved: {summary.approved}  Skipped: {summary.skipped}  "
        f"Reviewed: {summary.reviewed}\n"
    )
    return summary
