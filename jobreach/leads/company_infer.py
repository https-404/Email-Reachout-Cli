import re


COMMON_SECOND_LEVELS = {"co", "com", "org", "net", "ac", "gov"}


def infer_company_from_email(email: str) -> str:
    domain = email.split("@", 1)[-1].lower().strip()
    domain = domain.split(":")[0]
    parts = [part for part in domain.split(".") if part]
    if not parts:
        return ""
    stem = parts[-3] if len(parts) >= 3 and parts[-2] in COMMON_SECOND_LEVELS else parts[-2] if len(parts) >= 2 else parts[0]
    words = re.split(r"[-_]+", stem)
    return " ".join(word.capitalize() for word in words if word)
