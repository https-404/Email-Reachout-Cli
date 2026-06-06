from jobreach.core.models import EmailDraft


def dedupe_drafts(drafts: list[EmailDraft]) -> list[EmailDraft]:
    seen: set[str] = set()
    result: list[EmailDraft] = []
    for draft in drafts:
        key = str(draft.email).lower()
        if key not in seen:
            seen.add(key)
            result.append(draft)
    return result
