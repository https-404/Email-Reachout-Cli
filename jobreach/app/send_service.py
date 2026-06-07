from jobreach.core.models import EmailDraft, SendResult
from jobreach.logs.sent_log import SentLog
from jobreach.safety.rate_limit import wait_between_sends
from jobreach.safety.send_guard import can_send_draft
from jobreach.utils.time import utc_now_iso


class SendService:
    def __init__(self, gmail_client, sent_log: SentLog):
        self.gmail_client = gmail_client
        self.sent_log = sent_log

    def send_drafts(
        self,
        drafts: list[EmailDraft],
        confirm: bool,
        limit: int | None,
        delay_seconds: int,
        do_not_contact: set[str],
        force: bool = False,
        require_approved: bool = False,
        dry_run: bool = False,
        allow_high_risk: bool = False,
        on_sent=None,
    ) -> list[SendResult]:
        if not confirm:
            return [
                SendResult(draft_id=draft.id, email=draft.email, status="skipped", reason="missing confirmation")
                for draft in drafts[: limit or None]
            ]

        results: list[SendResult] = []
        sent_count = 0
        for draft in drafts:
            if limit is not None and sent_count >= limit:
                break
            already_sent = self.sent_log.has_been_sent(str(draft.email), draft.subject)
            allowed, reason = can_send_draft(
                draft,
                already_sent,
                do_not_contact,
                force=force,
                require_approved=require_approved,
                allow_high_risk=allow_high_risk,
            )
            if not allowed:
                draft.status = "skipped"
                results.append(SendResult(draft_id=draft.id, email=draft.email, status="skipped", reason=reason))
                continue
            if dry_run:
                results.append(SendResult(draft_id=draft.id, email=draft.email, status="sent", reason="dry-run"))
                sent_count += 1
                continue
            try:
                message_id = self.gmail_client.send_email(str(draft.email), draft.subject, draft.body)
                self.sent_log.record_sent(str(draft.email), draft.subject, draft.id, message_id)
                draft.status = "sent"
                draft.sent_at = utc_now_iso()
                sent_count += 1
                if on_sent:
                    on_sent(draft, message_id)
                results.append(
                    SendResult(
                        draft_id=draft.id,
                        email=draft.email,
                        status="sent",
                        reason="ok",
                        gmail_message_id=message_id,
                    )
                )
                if limit is None or sent_count < limit:
                    wait_between_sends(delay_seconds)
            except Exception as exc:
                draft.status = "failed"
                draft.error = str(exc)
                results.append(SendResult(draft_id=draft.id, email=draft.email, status="failed", reason=str(exc)))
        return results
