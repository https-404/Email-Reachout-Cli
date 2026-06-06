from jobreach.core.models import EmailDraft
from jobreach.drafts.reviewer import display_drafts


def review_drafts(drafts: list[EmailDraft]) -> None:
    display_drafts(drafts)
