from jobreach.ai.model_discovery.cache import get_cached_models, save_cached_models
from jobreach.ai.model_discovery.factory import ModelDiscoveryFactory
from jobreach.ai.provider_registry import PROVIDERS, get_provider
from jobreach.config.secrets import SecretStore
from jobreach.config.settings import SettingsStore
from jobreach.shell.prompts import choose_number, confirm, console, prompt_text


class ProviderSetupService:
    def __init__(
        self,
        settings_store: SettingsStore,
        secret_store: SecretStore,
    ):
        self.settings_store = settings_store
        self.secret_store = secret_store

    def setup_provider(self, allow_back: bool = False) -> bool:
        provider_id = self._choose_provider(allow_back=allow_back)
        if provider_id is None:
            return False

        info = get_provider(provider_id)
        console.print(
            f"\nPaste your API key below.\n"
            f"It will be stored locally using your operating system's secure keychain.\n"
            f"JobReach will not print or expose this key.\n"
        )
        api_key = prompt_text(f"Enter your {info.api_key_label}", password=True)
        if not api_key:
            console.print("[yellow]Cancelled.[/yellow]")
            return False

        console.print("\nChecking API key...")
        console.print("Fetching available models...")
        models, error = self._fetch_models(provider_id, api_key)
        if error and not models:
            console.print(f"[red]{error}[/red]")
            console.print(f"Try again with a new API key from:\n{info.api_key_help_url}")
            return False
        if error:
            console.print(f"[yellow]{error}[/yellow]")
            console.print("Showing recommended models instead.\n")

        model = self._choose_model(provider_id, models)
        if not model:
            console.print("[yellow]Cancelled.[/yellow]")
            return False

        self.secret_store.set_provider_key(provider_id, api_key)
        self.settings_store.update(
            default_provider=provider_id,
            default_model=model,
            first_run_complete=True,
        )
        save_cached_models(provider_id, models)
        console.print(f"\n[green]Default provider changed to {info.display_name}.[/green]")
        console.print(f"[green]Default model changed to {model}.[/green]")
        return True

    def update_api_key(self, provider_id: str | None = None) -> bool:
        settings = self.settings_store.load()
        provider_id = provider_id or settings.default_provider
        if not provider_id:
            return self.setup_provider()
        info = get_provider(provider_id)
        api_key = prompt_text(f"Enter new {info.api_key_label}", password=True)
        if not api_key:
            return False
        models, error = self._fetch_models(provider_id, api_key)
        if error and not models:
            console.print(f"[red]{error}[/red]")
            return False
        self.secret_store.set_provider_key(provider_id, api_key)
        if models:
            save_cached_models(provider_id, models)
        console.print("[green]API key updated.[/green]")
        return True

    def change_model(self) -> bool:
        settings = self.settings_store.load()
        if not settings.default_provider:
            console.print("[yellow]No provider configured. Run change provider first.[/yellow]")
            return False
        provider_id = settings.default_provider
        info = get_provider(provider_id)
        console.print(f"\nCurrent provider: {info.display_name}\n")
        console.print("Fetching available models...")
        api_key = self.secret_store.get_provider_key(provider_id)
        if not api_key:
            console.print("[red]Missing API key for current provider.[/red]")
            return False
        models, error = self._fetch_models(provider_id, api_key)
        if error and not models:
            console.print(f"[red]{error}[/red]")
            return False
        model = self._choose_model(provider_id, models)
        if not model:
            return False
        self.settings_store.update(default_model=model)
        console.print(f"[green]Default model changed to {model}.[/green]")
        return True

    def list_models_for_current(self, refresh: bool = False) -> list[str]:
        settings = self.settings_store.load()
        if not settings.default_provider:
            return []
        provider_id = settings.default_provider
        if not refresh:
            cached = get_cached_models(provider_id)
            if cached:
                return cached
        api_key = self.secret_store.get_provider_key(provider_id)
        if not api_key:
            return list(get_provider(provider_id).recommended_models)
        models, _ = self._fetch_models(provider_id, api_key)
        return models

    def _choose_provider(self, allow_back: bool = False) -> str | None:
        console.print(
            "\nChoose the AI provider JobReach should use to generate outreach drafts.\n"
            "You can change this later from settings.\n"
        )
        console.print("Choose an AI provider:\n")
        console.print("1. OpenAI")
        console.print("2. Google Gemini")
        console.print("3. Anthropic Claude")
        if allow_back:
            console.print("4. Back\n")
            choice = choose_number("Select provider", 4)
            if choice == 4:
                return None
        else:
            console.print("4. Skip for now\n")
            choice = choose_number("Select provider", 4)
            if choice == 4:
                return None
        mapping = {1: "openai", 2: "gemini", 3: "anthropic"}
        return mapping.get(choice or 0)

    def _fetch_models(self, provider_id: str, api_key: str) -> tuple[list[str], str | None]:
        info = get_provider(provider_id)
        try:
            client = ModelDiscoveryFactory.create(provider_id)
            models = client.list_models(api_key)
            if models:
                return models, None
            return list(info.recommended_models), "No models returned; using recommended list."
        except Exception as exc:
            message = str(exc).lower()
            if "401" in message or "unauthorized" in message or "invalid" in message or "api key" in message:
                return [], f"API key was rejected for {info.display_name}."
            if "network" in message or "connection" in message:
                return list(info.recommended_models), f"Network error while fetching models: {exc}"
            return list(info.recommended_models), f"Could not fetch models from {info.display_name}. Reason: {exc}"

    def _choose_model(self, provider_id: str, models: list[str]) -> str | None:
        info = get_provider(provider_id)
        recommended = [model for model in info.recommended_models if model in models]
        other = [model for model in models if model not in recommended]
        ordered = recommended + other
        if not ordered:
            ordered = list(info.recommended_models)

        console.print(f"\nAvailable {info.display_name} models:\n")
        if recommended:
            console.print("Recommended models:\n")
            for index, model in enumerate(recommended, start=1):
                console.print(f"{index}. {model}")
            offset = len(recommended)
            if other:
                console.print("\nOther available models:\n")
                for index, model in enumerate(other, start=offset + 1):
                    console.print(f"{index}. {model}")
        else:
            for index, model in enumerate(ordered, start=1):
                console.print(f"{index}. {model}")

        console.print(
            "\nChoose the model JobReach should use by default.\n"
            "You can change this later from settings.\n"
        )
        choice = choose_number("Choose default model", len(ordered))
        if not choice:
            return None
        return ordered[choice - 1]
