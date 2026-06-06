from pydantic import EmailStr, TypeAdapter, ValidationError

from jobreach.core.models import EmailDraft

EMAIL_ADAPTER = TypeAdapter(EmailStr)


def can_send_draft(
    draft: EmailDraft,
    already_sent: bool,
    do_not_contact: set[str],
    force: bool = False,
    require_approved: bool = False,
) -> tuple[bool, str]:
    email = str(draft.email).lower()
    try:
        EMAIL_ADAPTER.validate_python(email)
    except ValidationError:
        return False, "invalid email"
    if email in do_not_contact:
        return False, "email is do-not-contact"
    if already_sent and not force:
        return False, "already sent"
    if draft.status == "sent" and not force:
        return False, "draft already marked sent"
    if require_approved and draft.status != "approved" and not force:
        return False, "draft not approved"
    if draft.risk == "high":
        return False, "high-risk draft"
    if not draft.subject.strip() or not draft.body.strip():
        return False, "missing subject or body"
    return True, "ok"
