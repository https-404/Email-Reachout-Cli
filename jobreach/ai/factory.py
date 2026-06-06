import os

from jobreach.ai.base import AIClient
from jobreach.ai.langchain_client import LangChainAIClient
from jobreach.config.secrets import SecretStore
from jobreach.config.settings import AppSettings
from jobreach.core.constants import SUPPORTED_AI_PROVIDERS
from jobreach.core.errors import AIProviderError, ConfigError


class AIClientFactory:
    @staticmethod
    def from_settings(settings: AppSettings, secrets: SecretStore) -> AIClient:
        provider = settings.default_provider
        model = settings.default_model
        if not provider or not model:
            raise ConfigError("AI provider and model are not configured. Run: settings")
        api_key = secrets.get_provider_key(provider)
        if not api_key:
            raise ConfigError(f"Missing API key for {provider}. Run: settings")
        return LangChainAIClient(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=settings.temperature,
        )

    @staticmethod
    def create(provider: str, model: str, temperature: float = 0.4) -> AIClient:
        if provider not in SUPPORTED_AI_PROVIDERS:
            raise AIProviderError(f"Unsupported provider: {provider}")
        api_key = _legacy_env_api_key(provider)
        if not api_key:
            raise AIProviderError(
                f"Missing API key for {provider}. Set the provider env var or use the interactive shell."
            )
        return LangChainAIClient(provider=provider, model=model, api_key=api_key, temperature=temperature)


def _legacy_env_api_key(provider: str) -> str | None:
    mapping = {
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    env_name = mapping.get(provider)
    return os.getenv(env_name) if env_name else None
