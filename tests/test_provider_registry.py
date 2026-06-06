from jobreach.ai.provider_registry import PROVIDERS, get_provider


def test_provider_registry_has_all_providers():
    assert set(PROVIDERS.keys()) == {"openai", "gemini", "anthropic"}


def test_provider_registry_fields():
    openai = get_provider("openai")
    assert openai.display_name == "OpenAI"
    assert openai.default_model
    assert openai.recommended_models
