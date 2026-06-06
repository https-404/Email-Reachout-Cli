import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


DEFAULT_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-1.5-flash"


def get_data_dir() -> Path:
    return Path(os.getenv("JOBREACH_DATA_DIR", ".jobreach"))


def get_default_provider() -> str:
    return os.getenv("JOBREACH_AI_PROVIDER", DEFAULT_PROVIDER)


def get_default_model() -> str:
    return os.getenv("JOBREACH_AI_MODEL", DEFAULT_MODEL)


def get_default_delay_seconds() -> int:
    raw = os.getenv("JOBREACH_DEFAULT_DELAY_SECONDS", "15")
    try:
        return int(raw)
    except ValueError:
        return 15


def provider_env_status() -> dict[str, bool]:
    return {
        "Gemini": bool(os.getenv("GEMINI_API_KEY")),
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "Anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
    }
