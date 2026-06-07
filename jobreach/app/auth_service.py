from jobreach.config.settings import SettingsStore
from jobreach.mail.gmail_auth import (
    GmailAuthMethod,
    authenticate_gmail,
    complete_manual_gmail_flow,
    get_gmail_email,
    gmail_connected,
    logout_gmail,
    start_manual_gmail_flow,
)
from jobreach.shell.prompts import confirm, console, normalize_oauth_code, prompt_text


def choose_gmail_auth_method() -> GmailAuthMethod | None:
    console.print("\nHow would you like to connect Gmail?\n")
    console.print("1. Open browser automatically (recommended)")
    console.print("2. Copy sign-in link and paste authorization code")
    console.print("3. Cancel\n")
    raw = prompt_text("Choose option (1/2/3)")
    if raw == "1":
        return "browser"
    if raw == "2":
        return "manual"
    return None


def connect_gmail(settings_store: SettingsStore, method: GmailAuthMethod | None = None) -> bool:
    from jobreach.mail.credentials_bootstrap import ensure_oauth_client_secret

    console.print(
        "\nJobReach uses Gmail OAuth to send from your account.\n"
        "It does not ask for your Gmail password.\n"
        "Sign in with Google when prompted.\n"
    )
    try:
        ensure_oauth_client_secret()
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        return False
    if not confirm("Continue?", default=False):
        return False

    chosen = method or choose_gmail_auth_method()
    if not chosen:
        console.print("Cancelled.")
        return False

    try:
        if chosen == "browser":
            console.print("\nOpening browser for Google sign-in...")
            authenticate_gmail(method="browser")
        else:
            flow, auth_url = start_manual_gmail_flow()
            console.print("\n[bold]Manual sign-in[/bold]\n")
            console.print("1. Open this URL in your browser:\n")
            console.print(f"{auth_url}\n")
            console.print("2. Sign in and approve access.")
            console.print("3. Copy the authorization code (or full redirect URL) and paste it below.\n")
            raw_code = prompt_text("Authorization code")
            code = normalize_oauth_code(raw_code)
            if not code:
                console.print("[red]No code provided.[/red]")
                return False
            complete_manual_gmail_flow(flow, code)
    except Exception as exc:
        console.print(f"[red]Gmail connection failed:[/red] {exc}")
        console.print("\nTry again with: auth gmail")
        console.print("If the browser method fails, choose option 2 (manual link + code).")
        return False

    settings_store.update(gmail_connected_hint=True)
    email = get_gmail_email()
    console.print("[green]Gmail connected successfully.[/green]")
    if email:
        console.print(f"Signed in as: {email}")
    return True


class AuthService:
    def gmail(self, method: GmailAuthMethod = "browser", code: str | None = None):
        return authenticate_gmail(method=method, code=code)

    def status(self) -> bool:
        return gmail_connected()

    def logout(self) -> bool:
        return logout_gmail()
