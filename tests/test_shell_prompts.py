from jobreach.shell.prompts import choose_menu_option, normalize_oauth_code


def test_normalize_oauth_code_bare():
    assert normalize_oauth_code("abc123") == "abc123"


def test_normalize_oauth_code_from_url():
    url = "http://localhost/?code=abc123&scope=email"
    assert normalize_oauth_code(url) == "abc123"


def test_choose_menu_option_accepts_alias(monkeypatch):
    inputs = iter(["gmail"])
    monkeypatch.setattr("jobreach.shell.prompts.prompt_text", lambda message, default="": next(inputs))
    choice = choose_menu_option("Choose", 10, {"gmail": 5})
    assert choice == 5


def test_choose_menu_option_retries_invalid(monkeypatch):
    inputs = iter(["not-valid", "back"])
    monkeypatch.setattr("jobreach.shell.prompts.prompt_text", lambda message, default="": next(inputs))
    choice = choose_menu_option("Choose", 10, {"back": 10})
    assert choice == 10
