from pathlib import Path
from urllib.parse import parse_qs, urlparse

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console

console = Console()
_prompt_style = Style.from_dict({"prompt": "bold"})


def prompt_text(message: str, default: str = "", password: bool = False) -> str:
    session = PromptSession()
    suffix = f" [{default}]" if default and not password else ""
    result = session.prompt(
        f"{message}{suffix}: ",
        default=default,
        is_password=password,
        style=_prompt_style,
    )
    return result.strip()


def confirm(message: str, default: bool = False) -> bool:
    default_label = "Y/n" if default else "y/N"
    raw = prompt_text(f"{message} [{default_label}]", default="")
    if not raw:
        return default
    return raw.lower() in {"y", "yes"}


def confirm_send() -> bool:
    raw = prompt_text("Type SEND to confirm")
    return raw == "SEND"


def choose_number(message: str, max_option: int) -> int | None:
    raw = prompt_text(message)
    if not raw:
        return None
    try:
        choice = int(raw)
    except ValueError:
        console.print("[red]Please enter a number.[/red]")
        return None
    if choice < 1 or choice > max_option:
        console.print(f"[red]Choose a number between 1 and {max_option}.[/red]")
        return None
    return choice


def choose_menu_option(
    message: str,
    max_option: int,
    aliases: dict[str, int] | None = None,
    hint: str | None = None,
) -> int | None:
    """Read a menu choice by number or text alias. Loops until valid or empty input."""
    alias_map = {key.lower(): value for key, value in (aliases or {}).items()}
    if hint:
        console.print(hint)
    while True:
        raw = prompt_text(message)
        if not raw:
            return None
        normalized = " ".join(raw.lower().split())
        if normalized in alias_map:
            return alias_map[normalized]
        try:
            choice = int(normalized)
        except ValueError:
            console.print(
                "[red]Invalid choice.[/red] Enter a number (1–"
                f"{max_option}) or an option name (e.g. 'back', 'gmail')."
            )
            continue
        if choice < 1 or choice > max_option:
            console.print(f"[red]Choose a number between 1 and {max_option}.[/red]")
            continue
        return choice


def expand_path(path: str) -> Path:
    return Path(path.strip().strip('"').strip("'")).expanduser().resolve()


def normalize_oauth_code(raw: str) -> str:
    """Accept a bare code or a full redirect URL pasted from the browser."""
    text = raw.strip()
    if not text:
        return text
    if text.startswith("http://") or text.startswith("https://"):
        query = parse_qs(urlparse(text).query)
        if query.get("code"):
            return query["code"][0]
    if "code=" in text:
        query = parse_qs(text.lstrip("?"))
        if query.get("code"):
            return query["code"][0]
    return text
