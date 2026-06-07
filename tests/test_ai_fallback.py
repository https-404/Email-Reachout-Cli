from jobreach.ai.factory import AIClientFactory
from jobreach.ai.fallback import FallbackAIClient
from jobreach.config.settings import AppSettings
from jobreach.config.secrets import SecretStore


def test_factory_fallback_when_enabled(tmp_path, monkeypatch):
    settings = AppSettings(
        default_provider="openai",
        default_model="gpt-4o-mini",
        enable_provider_fallback=True,
        fallback_provider="anthropic",
        fallback_model="claude-3-5-haiku-latest",
    )
    secrets = SecretStore()

    def fake_key(provider):
        return f"key-{provider}"

    monkeypatch.setattr(secrets, "get_provider_key", fake_key)
    client = AIClientFactory.from_settings(settings, secrets)
    assert isinstance(client, FallbackAIClient)
