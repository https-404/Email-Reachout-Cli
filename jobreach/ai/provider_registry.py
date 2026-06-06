from pydantic import BaseModel


class ProviderInfo(BaseModel):
    id: str
    display_name: str
    api_key_label: str
    api_key_help_url: str
    supports_model_listing: bool
    recommended_models: list[str]
    default_model: str


PROVIDERS: dict[str, ProviderInfo] = {
    "openai": ProviderInfo(
        id="openai",
        display_name="OpenAI",
        api_key_label="OpenAI API key",
        api_key_help_url="https://platform.openai.com/api-keys",
        supports_model_listing=True,
        recommended_models=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
        default_model="gpt-4o-mini",
    ),
    "gemini": ProviderInfo(
        id="gemini",
        display_name="Google Gemini",
        api_key_label="Gemini API key",
        api_key_help_url="https://aistudio.google.com/app/apikey",
        supports_model_listing=True,
        recommended_models=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
        default_model="gemini-1.5-flash",
    ),
    "anthropic": ProviderInfo(
        id="anthropic",
        display_name="Anthropic Claude",
        api_key_label="Anthropic API key",
        api_key_help_url="https://console.anthropic.com/settings/keys",
        supports_model_listing=True,
        recommended_models=["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest"],
        default_model="claude-3-5-haiku-latest",
    ),
}


def get_provider(provider_id: str) -> ProviderInfo:
    if provider_id not in PROVIDERS:
        raise KeyError(f"Unknown provider: {provider_id}")
    return PROVIDERS[provider_id]
