from jobreach.app.auth_service import AuthService, connect_gmail
from jobreach.app.provider_setup_service import ProviderSetupService
from jobreach.config.paths import data_dir
from jobreach.config.secrets import SecretStore
from jobreach.config.settings import SettingsStore
from jobreach.shell.prompts import choose_menu_option, confirm, console, prompt_text

SETTINGS_ALIASES = {
    "1": 1,
    "provider": 1,
    "change provider": 1,
    "2": 2,
    "model": 2,
    "change model": 2,
    "3": 3,
    "api key": 3,
    "update api key": 3,
    "key": 3,
    "4": 4,
    "temperature": 4,
    "5": 5,
    "gmail": 5,
    "auth gmail": 5,
    "connect gmail": 5,
    "email": 5,
    "6": 6,
    "delay": 6,
    "send delay": 6,
    "7": 7,
    "data": 7,
    "data directory": 7,
    "8": 8,
    "storage": 8,
    "9": 9,
    "reset": 9,
    "10": 10,
    "back": 10,
    "exit": 10,
    "quit": 10,
    "cancel": 10,
}

GMAIL_ALIASES = {
    "1": 1,
    "connect": 1,
    "browser": 1,
    "auth": 1,
    "auth gmail": 1,
    "2": 2,
    "manual": 2,
    "code": 2,
    "link": 2,
    "paste": 2,
    "3": 3,
    "disconnect": 3,
    "logout": 3,
    "logout gmail": 3,
    "4": 4,
    "back": 4,
    "cancel": 4,
}


def run_settings_menu(
    settings_store: SettingsStore,
    secret_store: SecretStore,
    provider_setup: ProviderSetupService,
) -> None:
    menu_hint = "Enter a number or name (e.g. 'gmail', 'provider', 'back')."
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

        choice = choose_menu_option("Choose an option", 10, SETTINGS_ALIASES, menu_hint)
        if choice is None or choice == 10:
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
    menu_hint = "Enter a number or name (e.g. 'connect', 'manual', 'back')."
    while True:
        console.print("\n[bold]Gmail[/bold]\n")
        console.print("1. Connect Gmail (open browser)")
        console.print("2. Connect Gmail (copy link + paste code)")
        console.print("3. Disconnect Gmail")
        console.print("4. Back\n")

        choice = choose_menu_option("Choose an option", 4, GMAIL_ALIASES, menu_hint)
        if choice is None or choice == 4:
            return
        if choice == 1:
            connect_gmail(settings_store, method="browser")
        elif choice == 2:
            connect_gmail(settings_store, method="manual")
        elif choice == 3:
            removed = AuthService().logout()
            settings_store.update(gmail_connected_hint=False)
            console.print("Gmail disconnected." if removed else "No Gmail token found.")
