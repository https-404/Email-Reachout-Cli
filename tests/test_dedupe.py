from jobreach.core.models import EmailDraft
from jobreach.safety.dedupe import dedupe_drafts


def test_dedupe_drafts():
    draft = EmailDraft(id="1", email="a@example.com", recipient_type="unknown", subject="S", body="B")
    dupe = EmailDraft(id="2", email="a@example.com", recipient_type="unknown", subject="S2", body="B2")
    assert len(dedupe_drafts([draft, dupe])) == 1
