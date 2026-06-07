from typing import Literal

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from jobreach.config.paths import ensure_data_dirs, gmail_token_path
from jobreach.core.errors import GmailAuthError
from jobreach.mail.credentials_bootstrap import ensure_oauth_client_secret

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
GmailAuthMethod = Literal["browser", "manual"]


def _load_client_secret_flow() -> InstalledAppFlow:
    secret_path = ensure_oauth_client_secret()
    return InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)


def _save_credentials(creds: Credentials, token_path) -> Credentials:
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def authenticate_gmail_browser() -> Credentials:
    flow = _load_client_secret_flow()
    creds = flow.run_local_server(port=0, open_browser=True)
    return _save_credentials(creds, gmail_token_path())


def start_manual_gmail_flow() -> tuple[InstalledAppFlow, str]:
    flow = _load_client_secret_flow()
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true",
    )
    return flow, auth_url


def complete_manual_gmail_flow(flow: InstalledAppFlow, code: str) -> Credentials:
    flow.fetch_token(code=code)
    if not flow.credentials:
        raise GmailAuthError("Google did not return credentials. Check the code and try again.")
    return _save_credentials(flow.credentials, gmail_token_path())


def authenticate_gmail(method: GmailAuthMethod = "browser", code: str | None = None) -> Credentials:
    ensure_data_dirs()
    token_path = gmail_token_path()
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        return _save_credentials(creds, token_path)

    if method == "manual":
        raise GmailAuthError(
            "Manual Gmail sign-in requires an active OAuth flow. Use connect_gmail() from the shell."
        )

    return authenticate_gmail_browser()


def gmail_connected() -> bool:
    token_path = gmail_token_path()
    if not token_path.exists():
        return False
    try:
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        return bool(creds and (creds.valid or creds.refresh_token))
    except Exception:
        return False


def get_gmail_email() -> str | None:
    if not gmail_connected():
        return None
    try:
        creds = authenticate_gmail()
        from googleapiclient.discovery import build

        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("emailAddress")
    except Exception:
        return None


def logout_gmail() -> bool:
    token_path = gmail_token_path()
    if token_path.exists():
        token_path.unlink()
        return True
    return False
