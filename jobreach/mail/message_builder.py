import base64
from email.message import EmailMessage


def build_gmail_raw_message(to_email: str, subject: str, body: str, reply_to: str | None = None) -> str:
    message = EmailMessage()
    message["To"] = to_email
    message["Subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(body)
    return base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
