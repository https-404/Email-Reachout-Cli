from jobreach.core.models import EmailDraft
from jobreach.app.send_service import SendService
from jobreach.logs.sent_log import SentLog


class FakeGmail:
    def send_email(self, email, subject, body):
        raise AssertionError("should not call Gmail in dry run")


def test_dry_run_send_no_api(tmp_path):
    sent_log = SentLog(path=tmp_path / "sent.csv")
    service = SendService(FakeGmail(), sent_log)
    draft = EmailDraft(
        id="1",
        email="a@b.com",
        company="Co",
        recipient_type="hr",
        subject="Hi",
        body="Body",
        personalization_score=8,
        risk="low",
        status="approved",
    )
    results = service.send_drafts(
        [draft],
        confirm=True,
        limit=None,
        delay_seconds=0,
        do_not_contact=set(),
        require_approved=True,
        dry_run=True,
    )
    assert len(results) == 1
    assert results[0].status == "sent"
    assert results[0].reason == "dry-run"
