import keyring
import keyring.errors

from jobreach.core.errors import ConfigError


class SecretStore:
    SERVICE_NAME = "jobreach"

    def __init__(self):
        self._verify_keyring()

    def _verify_keyring(self) -> None:
        try:
            keyring.set_password(self.SERVICE_NAME, "__probe__", "test")
            keyring.delete_password(self.SERVICE_NAME, "__probe__")
        except keyring.errors.KeyringError as exc:
            raise ConfigError(
                "Secure key storage is not available on this system.\n"
                "JobReach cannot save API keys safely.\n"
                "Please install/configure your OS keyring, then try again."
            ) from exc

    def _account(self, provider: str) -> str:
        return f"provider:{provider}"

    def set_provider_key(self, provider: str, api_key: str) -> None:
        keyring.set_password(self.SERVICE_NAME, self._account(provider), api_key)

    def get_provider_key(self, provider: str) -> str | None:
        return keyring.get_password(self.SERVICE_NAME, self._account(provider))

    def delete_provider_key(self, provider: str) -> None:
        try:
            keyring.delete_password(self.SERVICE_NAME, self._account(provider))
        except keyring.errors.PasswordDeleteError:
            pass

    def has_provider_key(self, provider: str) -> bool:
        return bool(self.get_provider_key(provider))

    def key_hint(self, provider: str) -> str | None:
        key = self.get_provider_key(provider)
        if not key:
            return None
        if len(key) <= 4:
            return "****"
        return f"...{key[-4:]}"
