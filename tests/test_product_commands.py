from jobreach.shell.commands import resolve_command, COMMANDS


def test_product_commands_registered():
    for command in [
        "preview leads",
        "change tone",
        "campaigns",
        "follow up",
        "demo",
        "send queue run",
    ]:
        assert command in COMMANDS


def test_mark_replied_command_passthrough():
    assert resolve_command("mark replied user@example.com") == "mark replied user@example.com"
