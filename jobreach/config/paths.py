import os
import shutil
from pathlib import Path


DEFAULT_DATA_DIR = Path.home() / ".jobreach"


def _load_dotenv_if_needed() -> None:
    from dotenv import load_dotenv

    load_dotenv()


def get_data_dir() -> Path:
    _load_dotenv_if_needed()
    return Path(os.getenv("JOBREACH_DATA_DIR", str(DEFAULT_DATA_DIR)))


def data_dir() -> Path:
    return get_data_dir()


def config_dir() -> Path:
    return data_dir() / "config"


def settings_path() -> Path:
    return config_dir() / "settings.json"


def provider_models_cache_path() -> Path:
    return config_dir() / "provider_models_cache.json"


def credentials_dir() -> Path:
    return data_dir() / "credentials"


def google_client_secret_path() -> Path:
    return credentials_dir() / "google_client_secret.json"


def tokens_dir() -> Path:
    return data_dir() / "tokens"


def gmail_token_path() -> Path:
    return tokens_dir() / "gmail_token.json"


def drafts_dir() -> Path:
    return data_dir() / "drafts"


def drafts_index_path() -> Path:
    return drafts_dir() / "index.json"


def profiles_dir() -> Path:
    return data_dir() / "profiles"


def logs_dir() -> Path:
    return data_dir() / "logs"


def sent_log_path() -> Path:
    return logs_dir() / "sent_log.csv"


def run_log_path() -> Path:
    return logs_dir() / "run_log.jsonl"


def do_not_contact_path() -> Path:
    return data_dir() / "do_not_contact.csv"


def crm_dir() -> Path:
    return data_dir() / "crm"


def crm_db_path() -> Path:
    return crm_dir() / "jobreach.db"


def exports_dir() -> Path:
    return data_dir() / "exports"


def enrichment_cache_dir() -> Path:
    return data_dir() / "cache" / "enrichment"


def legacy_data_dir() -> Path:
    return Path.cwd() / ".jobreach"


def ensure_data_dirs() -> None:
    for path in (
        config_dir(),
        credentials_dir(),
        tokens_dir(),
        drafts_dir(),
        profiles_dir(),
        logs_dir(),
        crm_dir(),
        exports_dir(),
        enrichment_cache_dir(),
        data_dir() / "cache" / "profiles",
        data_dir() / "cache" / "generations",
    ):
        path.mkdir(parents=True, exist_ok=True)


def migrate_legacy_data_dir() -> bool:
    legacy = legacy_data_dir()
    target = DEFAULT_DATA_DIR
    if not legacy.exists() or not legacy.is_dir():
        return False
    if target.exists() and any(target.iterdir()):
        return False
    target.mkdir(parents=True, exist_ok=True)
    for item in legacy.iterdir():
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
    return True
