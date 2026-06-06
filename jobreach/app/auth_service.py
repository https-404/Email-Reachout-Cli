from jobreach.mail.gmail_auth import authenticate_gmail, gmail_connected, logout_gmail


class AuthService:
    def gmail(self):
        return authenticate_gmail()

    def status(self) -> bool:
        return gmail_connected()

    def logout(self) -> bool:
        return logout_gmail()
