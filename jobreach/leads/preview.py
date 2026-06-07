from dataclasses import dataclass

from pydantic import ValidationError

from jobreach.core.models import Lead
from jobreach.leads.loader import load_leads_csv


@dataclass
class LeadLoadStats:
    valid: int
    invalid_skipped: int
    duplicates_skipped: int


def load_leads_with_stats(path: str) -> tuple[list[Lead], LeadLoadStats]:
    """Load leads and report how many rows were skipped."""
    import csv
    from pathlib import Path

    from jobreach.leads.company_infer import infer_company_from_email
    from jobreach.leads.recipient_type import detect_recipient_type

    source = Path(path)
    valid_leads: list[Lead] = []
    seen: set[str] = set()
    invalid_skipped = 0
    duplicates_skipped = 0

    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            cleaned = {k.strip(): (v or "").strip() for k, v in row.items() if k}
            email = cleaned.get("email", "").lower()
            if not email:
                invalid_skipped += 1
                continue
            if email in seen:
                duplicates_skipped += 1
                continue
            cleaned["email"] = email
            cleaned["company"] = cleaned.get("company") or infer_company_from_email(email)
            cleaned["recipient_type"] = cleaned.get("recipient_type") or detect_recipient_type(email)
            try:
                valid_leads.append(Lead(**cleaned))
                seen.add(email)
            except ValidationError:
                invalid_skipped += 1

    stats = LeadLoadStats(
        valid=len(valid_leads),
        invalid_skipped=invalid_skipped,
        duplicates_skipped=duplicates_skipped,
    )
    return valid_leads, stats
