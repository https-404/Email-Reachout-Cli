import base64

from jobreach.mail.message_builder import build_gmail_raw_message


def test_message_builder_base64_output():
    raw = build_gmail_raw_message("to@example.com", "Subject", "Body")
    decoded = base64.urlsafe_b64decode(raw.encode()).decode()
    assert "To: to@example.com" in decoded
    assert "Subject: Subject" in decoded
    assert "Body" in decoded
