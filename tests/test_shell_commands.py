from jobreach.shell.commands import ALIASES, COMMANDS, resolve_command
from jobreach.shell.prompts import confirm_send


def test_resolve_command_aliases():
    assert resolve_command("setup") == "settings"
    assert resolve_command("send") == "send emails"
    assert resolve_command("  Generate   Drafts ") == "generate drafts"


def test_commands_include_core_commands():
    for command in [
        "help",
        "status",
        "settings",
        "generate drafts",
        "review drafts",
        "send emails",
        "auth gmail",
    ]:
        assert command in COMMANDS


def test_aliases_map_to_existing_commands():
    for alias, target in ALIASES.items():
        assert target in COMMANDS or target in {"exit", "quit"}


def test_confirm_send_exact_match(monkeypatch):
    monkeypatch.setattr("jobreach.shell.prompts.prompt_text", lambda message: "SEND")
    assert confirm_send() is True

    monkeypatch.setattr("jobreach.shell.prompts.prompt_text", lambda message: "send")
    assert confirm_send() is False

    monkeypatch.setattr("jobreach.shell.prompts.prompt_text", lambda message: "y")
    assert confirm_send() is False
