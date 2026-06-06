from jobreach.app.auth_service import AuthService
from jobreach.app.provider_setup_service import ProviderSetupService
from jobreach.config.secrets import SecretStore
from jobreach.config.settings import SettingsStore
from jobreach.shell.prompts import confirm, console


class OnboardingService:
    def __init__(self, settings_store: SettingsStore, secret_store: SecretStore):
        self.settings_store = settings_store
        self.secret_store = secret_store
        self.provider_setup = ProviderSetupService(settings_store, secret_store)

    def needs_onboarding(self) -> bool:
        settings = self.settings_store.load()
        if not settings.first_run_complete:
            return True
        if not settings.default_provider or not settings.default_model:
            return True
        if settings.default_provider and not self.secret_store.has_provider_key(settings.default_provider):
            return True
        return False

    def run(self) -> None:
        console.print(
            "\n[bold]Welcome to JobReach.[/bold]\n\n"
            "JobReach helps you generate and send job outreach emails using your CV "
            "and public HR/company emails.\n\n"
            "Let's set up your AI provider.\n"
        )
        if not self.provider_setup.setup_provider():
            console.print("[yellow]Setup skipped. You can finish later with: settings[/yellow]")
            return

        if confirm("Would you like to connect Gmail now so JobReach can send emails?", default=False):
            console.print("\nOpening browser for Google sign-in...")
            try:
                AuthService().gmail()
                self.settings_store.update(gmail_connected_hint=True)
                console.print("[green]Gmail connected successfully.[/green]")
            except Exception as exc:
                console.print(f"[yellow]Gmail connection failed: {exc}[/yellow]")
                console.print("You can connect later with: auth gmail")

        self.settings_store.update(first_run_complete=True)
        console.print("\n[green]Setup complete.[/green]")
        console.print('Type "generate drafts" to start.\n')
