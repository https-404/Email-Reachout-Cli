import keyring
import pytest

from jobreach.config.secrets import SecretStore
from jobreach.core.errors import ConfigError


class MemoryKeyring:
    def __init__(self):
        self.passwords: dict[tuple[str, str], str] = {}

    def get_password(self, service, username):
        return self.passwords.get((service, username))

    def set_password(self, service, username, password):
        self.passwords[(service, username)] = password

    def delete_password(self, service, username):
        self.passwords.pop((service, username), None)


@pytest.fixture
def memory_keyring(monkeypatch):
    backend = MemoryKeyring()
    monkeypatch.setattr(keyring, "get_keyring", lambda: backend)
    monkeypatch.setattr(keyring, "set_password", backend.set_password)
    monkeypatch.setattr(keyring, "get_password", backend.get_password)
    monkeypatch.setattr(keyring, "delete_password", backend.delete_password)
    return backend


def test_secret_store_roundtrip(memory_keyring):
    store = SecretStore()
    store.set_provider_key("openai", "sk-test-key-1234")
    assert store.has_provider_key("openai")
    assert store.get_provider_key("openai") == "sk-test-key-1234"
    assert store.key_hint("openai") == "...1234"
    store.delete_provider_key("openai")
    assert not store.has_provider_key("openai")


def test_secret_store_missing_keyring(monkeypatch):
    def fail_set(*args, **kwargs):
        raise keyring.errors.KeyringError("no keyring")

    monkeypatch.setattr(keyring, "set_password", fail_set)
    with pytest.raises(ConfigError, match="Secure key storage"):
        SecretStore()
