from jobreach.shell.prompts import confirm_send_high_risk


def test_confirm_send_high_risk_exact(monkeypatch):
    monkeypatch.setattr("jobreach.shell.prompts.prompt_text", lambda message: "SEND HIGH RISK")
    assert confirm_send_high_risk() is True

    monkeypatch.setattr("jobreach.shell.prompts.prompt_text", lambda message: "SEND")
    assert confirm_send_high_risk() is False
