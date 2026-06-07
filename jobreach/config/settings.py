import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from jobreach.config.paths import settings_path
from jobreach.utils.json_utils import read_json, write_json


DEFAULT_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-1.5-flash"


class AppSettings(BaseModel):
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    temperature: float = 0.4
    send_delay_seconds: int = 15
    default_output_dir: str = "~/.jobreach/drafts"
    first_run_complete: bool = False
    gmail_connected_hint: bool = False
    last_cv_path: Optional[str] = None
    last_leads_path: Optional[str] = None
    tone_preset: str = "default"
    review_model: Optional[str] = None
    generate_model: Optional[str] = None
    ai_quality_check: bool = True
    daily_send_cap: int = 50
    send_window_start: str = "09:00"
    send_window_end: str = "17:00"
    follow_up_days: int = 7
    enrichment_enabled: bool = False
    enable_provider_fallback: bool = False
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None


class SettingsStore:
    def __init__(self, path: Path | None = None):
        self.path = path or settings_path()

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        data = read_json(self.path)
        return AppSettings.model_validate(data)

    def save(self, settings: AppSettings) -> None:
        write_json(self.path, settings.model_dump(mode="json"))

    def update(self, **kwargs) -> AppSettings:
        settings = self.load()
        updated = settings.model_copy(update=kwargs)
        self.save(updated)
        return updated


def _load_dotenv_if_needed() -> None:
    from dotenv import load_dotenv

    load_dotenv()


def get_default_provider() -> str:
    _load_dotenv_if_needed()
    return os.getenv("JOBREACH_AI_PROVIDER", DEFAULT_PROVIDER)


def get_default_model() -> str:
    _load_dotenv_if_needed()
    return os.getenv("JOBREACH_AI_MODEL", DEFAULT_MODEL)


def get_default_delay_seconds() -> int:
    _load_dotenv_if_needed()
    raw = os.getenv("JOBREACH_DEFAULT_DELAY_SECONDS", "15")
    try:
        return int(raw)
    except ValueError:
        return 15


def provider_env_status() -> dict[str, bool]:
    _load_dotenv_if_needed()
    return {
        "Gemini": bool(os.getenv("GEMINI_API_KEY")),
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "Anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
    }
