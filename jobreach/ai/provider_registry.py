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
    "openrouter": ProviderInfo(
        id="openrouter",
        display_name="OpenRouter",
        api_key_label="OpenRouter API key",
        api_key_help_url="https://openrouter.ai/keys",
        supports_model_listing=False,
        recommended_models=["openai/gpt-4o-mini", "anthropic/claude-3.5-haiku"],
        default_model="openai/gpt-4o-mini",
    ),
    "groq": ProviderInfo(
        id="groq",
        display_name="Groq",
        api_key_label="Groq API key",
        api_key_help_url="https://console.groq.com/keys",
        supports_model_listing=False,
        recommended_models=["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        default_model="llama-3.3-70b-versatile",
    ),
    "deepseek": ProviderInfo(
        id="deepseek",
        display_name="DeepSeek",
        api_key_label="DeepSeek API key",
        api_key_help_url="https://platform.deepseek.com/api_keys",
        supports_model_listing=False,
        recommended_models=["deepseek-chat"],
        default_model="deepseek-chat",
    ),
    "ollama": ProviderInfo(
        id="ollama",
        display_name="Ollama (local)",
        api_key_label="Ollama API key (optional)",
        api_key_help_url="https://ollama.com",
        supports_model_listing=False,
        recommended_models=["llama3.2", "mistral"],
        default_model="llama3.2",
    ),
}


def get_provider(provider_id: str) -> ProviderInfo:
    if provider_id not in PROVIDERS:
        raise KeyError(f"Unknown provider: {provider_id}")
    return PROVIDERS[provider_id]
