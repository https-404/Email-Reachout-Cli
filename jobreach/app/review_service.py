from dataclasses import dataclass

from jobreach.core.models import EmailDraft
from jobreach.drafts.reviewer import display_drafts
from jobreach.drafts.store import load_drafts, save_drafts
from jobreach.drafts.index import update_batch_stats
from jobreach.shell.prompts import choose_number, console
from jobreach.shell.render import print_draft


@dataclass
class ReviewSummary:
    approved: int = 0
    skipped: int = 0
    reviewed: int = 0


def review_drafts(drafts: list[EmailDraft]) -> None:
    display_drafts(drafts)


def interactive_review(batch_path: str, batch_id: str) -> ReviewSummary:
    drafts = load_drafts(batch_path)
    summary = ReviewSummary()
    index = 0
    total = len(drafts)

    while index < total:
        draft = drafts[index]
        print_draft(draft, index + 1, total)
        console.print(
            "Actions:\n"
            "1. Approve\n"
            "2. Skip\n"
            "3. Next\n"
            "4. Stop review\n"
        )
        choice = choose_number("Choose action", 4)
        if not choice or choice == 4:
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
            index += 1

    update_batch_stats(batch_id)
    console.print(
        f"\nReview complete. Approved: {summary.approved}  Skipped: {summary.skipped}  "
        f"Reviewed: {summary.reviewed}\n"
    )
    return summary
