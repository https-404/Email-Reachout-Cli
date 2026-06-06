from jobreach.leads.recipient_type import detect_recipient_type


def test_detect_recipient_type():
    assert detect_recipient_type("careers@example.com") == "hr"
    assert detect_recipient_type("cto@example.com") == "founder_or_exec"
    assert detect_recipient_type("hello@example.com") == "general"
    assert detect_recipient_type("person@example.com") == "unknown"
