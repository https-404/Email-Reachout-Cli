from jobreach.ai.provider_registry import PROVIDERS, get_provider


def test_provider_registry_has_all_providers():
    assert {"openai", "gemini", "anthropic"}.issubset(set(PROVIDERS.keys()))
    assert "openrouter" in PROVIDERS


def test_provider_registry_fields():
    openai = get_provider("openai")
    assert openai.display_name == "OpenAI"
    assert openai.default_model
    assert openai.recommended_models
