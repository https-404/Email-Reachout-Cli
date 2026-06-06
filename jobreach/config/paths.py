from pathlib import Path

from jobreach.config.settings import get_data_dir


def data_dir() -> Path:
    return get_data_dir()


def credentials_dir() -> Path:
    return data_dir() / "credentials"


def google_client_secret_path() -> Path:
    return credentials_dir() / "google_client_secret.json"


def tokens_dir() -> Path:
    return data_dir() / "tokens"


def gmail_token_path() -> Path:
    return tokens_dir() / "gmail_token.json"


def logs_dir() -> Path:
    return data_dir() / "logs"


def sent_log_path() -> Path:
    return logs_dir() / "sent_log.csv"


def run_log_path() -> Path:
    return logs_dir() / "run_log.jsonl"


def do_not_contact_path() -> Path:
    return data_dir() / "do_not_contact.csv"


def ensure_data_dirs() -> None:
    for path in (credentials_dir(), tokens_dir(), logs_dir(), data_dir() / "cache" / "profiles", data_dir() / "cache" / "generations"):
        path.mkdir(parents=True, exist_ok=True)
