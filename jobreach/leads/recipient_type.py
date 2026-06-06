HR_ALIASES = {"hr", "careers", "jobs", "talent", "recruiting", "recruitment"}
EXEC_ALIASES = {"founder", "ceo", "cto", "cofounder", "co-founder"}
GENERAL_ALIASES = {"info", "contact", "hello", "support"}


def detect_recipient_type(email: str) -> str:
    local = email.split("@", 1)[0].lower()
    tokens = {part for sep in (".", "-", "_", "+") for part in local.replace(sep, " ").split()}
    tokens.add(local)
    if tokens & HR_ALIASES:
        return "hr"
    if tokens & EXEC_ALIASES:
        return "founder_or_exec"
    if tokens & GENERAL_ALIASES:
        return "general"
    return "unknown"
