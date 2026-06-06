from googleapiclient.discovery import build

from jobreach.mail.message_builder import build_gmail_raw_message


class GmailClient:
    def __init__(self, credentials):
        self.service = build("gmail", "v1", credentials=credentials)

    def send_email(self, to_email: str, subject: str, body: str) -> str:
        raw_message = build_gmail_raw_message(to_email, subject, body)
        result = self.service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return result["id"]
