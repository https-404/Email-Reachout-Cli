import pytest

from jobreach.ai.factory import AIClientFactory
from jobreach.config.secrets import SecretStore
from jobreach.config.settings import AppSettings
from jobreach.core.errors import AIProviderError, ConfigError


def test_ai_factory_rejects_unknown_provider():
    with pytest.raises(AIProviderError):
        AIClientFactory.create("bad", "model")


def test_from_settings_missing_api_key(monkeypatch, tmp_path):
    import keyring

    class MemoryKeyring:
        def get_password(self, service, username):
            return None

        def set_password(self, service, username, password):
            pass

        def delete_password(self, service, username):
            pass

    backend = MemoryKeyring()
    monkeypatch.setattr(keyring, "set_password", backend.set_password)
    monkeypatch.setattr(keyring, "get_password", backend.get_password)
    monkeypatch.setattr(keyring, "delete_password", backend.delete_password)

    settings = AppSettings(default_provider="openai", default_model="gpt-4o-mini")
    secrets = SecretStore()
    with pytest.raises(ConfigError, match="Missing API key"):
        AIClientFactory.from_settings(settings, secrets)
