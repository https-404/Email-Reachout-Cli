from jobreach.core.models import EmailDraft
from jobreach.safety.send_guard import can_send_draft


def test_send_guard_blocks_high_risk():
    draft = EmailDraft(id="1", email="a@example.com", recipient_type="unknown", subject="S", body="B", risk="high")
    allowed, reason = can_send_draft(draft, False, set())
    assert not allowed
    assert reason == "high-risk draft"
