from jobreach.app.auth_service import AuthService
from jobreach.app.onboarding_service import OnboardingService
from jobreach.app.provider_setup_service import ProviderSetupService
from jobreach.config.paths import data_dir, do_not_contact_path, ensure_data_dirs
from jobreach.config.secrets import SecretStore
from jobreach.config.settings import SettingsStore
from jobreach.shell.prompts import choose_number, confirm, console, prompt_text


def run_settings_menu(
    settings_store: SettingsStore,
    secret_store: SecretStore,
    provider_setup: ProviderSetupService,
) -> None:
    while True:
        settings = settings_store.load()
        provider_label = settings.default_provider or "Not set"
        model_label = settings.default_model or "Not set"
        gmail_label = "connected" if settings.gmail_connected_hint else "not connected"
        console.print("\n[bold]Settings[/bold]\n")
        console.print("AI")
        console.print(f"1. Current provider: {provider_label}")
        console.print(f"2. Current model: {model_label}")
        console.print("3. Update API key")
        console.print(f"4. Change temperature: {settings.temperature}")
        console.print("\nEmail")
        console.print(f"5. Gmail: {gmail_label}")
        console.print(f"6. Send delay: {settings.send_delay_seconds} seconds")
        console.print("\nStorage")
        console.print(f"7. Data directory: {data_dir()}")
        console.print("8. Open data directory info")
        console.print("\nOther")
        console.print("9. Reset first-run setup")
        console.print("10. Back\n")

        choice = choose_number("Choose an option", 10)
        if not choice or choice == 10:
            return
        if choice == 1:
            provider_setup.setup_provider(allow_back=True)
        elif choice == 2:
            provider_setup.change_model()
        elif choice == 3:
            provider_setup.update_api_key()
        elif choice == 4:
            raw = prompt_text("Temperature", default=str(settings.temperature))
            try:
                settings_store.update(temperature=float(raw))
                console.print("[green]Temperature updated.[/green]")
            except ValueError:
                console.print("[red]Invalid number.[/red]")
        elif choice == 5:
            _gmail_settings_menu(settings_store)
        elif choice == 6:
            raw = prompt_text("Send delay seconds", default=str(settings.send_delay_seconds))
            try:
                settings_store.update(send_delay_seconds=int(raw))
                console.print("[green]Send delay updated.[/green]")
            except ValueError:
                console.print("[red]Invalid number.[/red]")
        elif choice == 7:
            console.print(f"\nData directory: {data_dir()}\n")
        elif choice == 8:
            console.print(f"\nJobReach stores local data at:\n{data_dir()}\n")
        elif choice == 9:
            if confirm("Reset first-run setup?", default=False):
                settings_store.update(first_run_complete=False)
                console.print("[green]First-run setup reset. Restart JobReach to onboard again.[/green]")


def _gmail_settings_menu(settings_store: SettingsStore) -> None:
    from jobreach.app.auth_service import AuthService
    from jobreach.mail.gmail_auth import get_gmail_email

    console.print("\n1. Connect Gmail")
    console.print("2. Disconnect Gmail")
    console.print("3. Back\n")
    choice = choose_number("Choose an option", 3)
    if choice == 1:
        console.print(
            "\nJobReach uses Gmail OAuth to send from your account.\n"
            "It does not ask for your Gmail password.\n"
        )
        if confirm("Continue?", default=False):
            console.print("\nOpening browser for Google sign-in...")
            AuthService().gmail()
            settings_store.update(gmail_connected_hint=True)
            email = get_gmail_email()
            console.print("[green]Gmail connected successfully.[/green]")
            if email:
                console.print(f"Signed in as: {email}")
    elif choice == 2:
        removed = AuthService().logout()
        settings_store.update(gmail_connected_hint=False)
        console.print("Gmail disconnected." if removed else "No Gmail token found.")
