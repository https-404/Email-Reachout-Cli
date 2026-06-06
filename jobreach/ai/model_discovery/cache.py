from datetime import datetime, timezone
from pathlib import Path

from jobreach.config.paths import provider_models_cache_path
from jobreach.utils.json_utils import read_json, write_json


def _cache_path() -> Path:
    return provider_models_cache_path()


def get_cached_models(provider: str) -> list[str] | None:
    path = _cache_path()
    if not path.exists():
        return None
    data = read_json(path)
    entry = data.get(provider)
    if not entry:
        return None
    return entry.get("models")


def save_cached_models(provider: str, models: list[str]) -> None:
    path = _cache_path()
    data = read_json(path) if path.exists() else {}
    data[provider] = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "models": models,
    }
    write_json(path, data)
