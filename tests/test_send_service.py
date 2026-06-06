from jobreach.app.send_service import SendService
from jobreach.core.models import EmailDraft
from jobreach.logs.sent_log import SentLog


class FakeGmailClient:
    def send_email(self, to_email, subject, body):
        return "fake-message-id"


def test_send_service_requires_confirm(tmp_path):
    service = SendService(FakeGmailClient(), SentLog(tmp_path / "sent.csv"))
    draft = EmailDraft(id="1", email="a@example.com", recipient_type="unknown", subject="S", body="B", risk="low")
    results = service.send_drafts([draft], confirm=False, limit=None, delay_seconds=0, do_not_contact=set())
    assert results[0].status == "skipped"


def test_send_service_sends_with_confirm(tmp_path):
    service = SendService(FakeGmailClient(), SentLog(tmp_path / "sent.csv"))
    draft = EmailDraft(id="1", email="a@example.com", recipient_type="unknown", subject="S", body="B", risk="low")
    results = service.send_drafts([draft], confirm=True, limit=1, delay_seconds=0, do_not_contact=set())
    assert results[0].status == "sent"
    assert draft.status == "sent"
