from jobreach.safety.send_guard import can_send_draft
from jobreach.core.models import EmailDraft


def test_high_risk_blocked_by_default():
    draft = EmailDraft(
        id="1",
        email="a@b.com",
        company="Co",
        recipient_type="hr",
        subject="Hi",
        body="Body",
        personalization_score=3,
        risk="high",
        status="approved",
    )
    allowed, reason = can_send_draft(draft, False, set(), require_approved=True)
    assert not allowed
    assert reason == "high-risk draft"


def test_high_risk_allowed_with_flag():
    draft = EmailDraft(
        id="1",
        email="a@b.com",
        company="Co",
        recipient_type="hr",
        subject="Hi",
        body="Body",
        personalization_score=3,
        risk="high",
        status="approved",
    )
    allowed, _ = can_send_draft(draft, False, set(), require_approved=True, allow_high_risk=True)
    assert allowed
