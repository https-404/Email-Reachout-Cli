from jobreach.core.models import Lead


def dedupe_leads(leads: list[Lead]) -> list[Lead]:
    seen: set[str] = set()
    result: list[Lead] = []
    for lead in leads:
        key = str(lead.email).lower()
        if key not in seen:
            seen.add(key)
            result.append(lead)
    return result
