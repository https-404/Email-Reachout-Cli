from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from jobreach.config.paths import ensure_data_dirs, gmail_token_path, google_client_secret_path
from jobreach.core.errors import GmailAuthError

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def authenticate_gmail() -> Credentials:
    ensure_data_dirs()
    token_path = gmail_token_path()
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds
    secret_path = google_client_secret_path()
    if not secret_path.exists():
        raise GmailAuthError(f"Missing Google OAuth client secret: {secret_path}")
    flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def gmail_connected() -> bool:
    token_path = gmail_token_path()
    if not token_path.exists():
        return False
    try:
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        return bool(creds and (creds.valid or creds.refresh_token))
    except Exception:
        return False


def logout_gmail() -> bool:
    token_path = gmail_token_path()
    if token_path.exists():
        token_path.unlink()
        return True
    return False
