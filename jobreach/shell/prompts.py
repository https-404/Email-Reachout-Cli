from pathlib import Path

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


def expand_path(path: str) -> Path:
    return Path(path.strip().strip('"').strip("'")).expanduser().resolve()
