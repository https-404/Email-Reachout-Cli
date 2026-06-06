import csv
from pathlib import Path

from pydantic import ValidationError

from jobreach.core.errors import LeadLoadError
from jobreach.core.models import Lead
from jobreach.leads.company_infer import infer_company_from_email
from jobreach.leads.recipient_type import detect_recipient_type


def _clean_row(row: dict[str, str | None]) -> dict[str, str]:
    return {key.strip(): (value or "").strip() for key, value in row.items() if key}


def load_leads_csv(path: str) -> list[Lead]:
    source = Path(path)
    if not source.exists():
        raise LeadLoadError(f"Leads CSV not found: {path}")

    leads: list[Lead] = []
    seen: set[str] = set()
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "email" not in {field.strip() for field in reader.fieldnames}:
            raise LeadLoadError("Leads CSV must include an email column")
        for row in reader:
            cleaned = _clean_row(row)
            email = cleaned.get("email", "").lower()
            if not email or all(not value for value in cleaned.values()):
                continue
            if email in seen:
                continue
            cleaned["email"] = email
            cleaned["company"] = cleaned.get("company") or infer_company_from_email(email)
            cleaned["recipient_type"] = cleaned.get("recipient_type") or detect_recipient_type(email)
            try:
                leads.append(Lead(**cleaned))
                seen.add(email)
            except ValidationError:
                continue
    return leads
