import csv
import json
from pathlib import Path

from jobreach.core.models import EmailDraft
from jobreach.utils.files import ensure_parent

FIELDS = [
    "id",
    "email",
    "company",
    "recipient_name",
    "recipient_type",
    "subject",
    "body",
    "personalization_score",
    "risk",
    "warnings",
    "status",
    "sent_at",
    "error",
    "provider",
    "model",
]


def save_drafts(path: str, drafts: list[EmailDraft]) -> None:
    ensure_parent(path)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for draft in drafts:
            row = draft.model_dump(mode="json")
            row["warnings"] = json.dumps(row.get("warnings", []))
            writer.writerow({field: row.get(field, "") for field in FIELDS})


def load_drafts(path: str) -> list[EmailDraft]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        drafts: list[EmailDraft] = []
        for row in csv.DictReader(handle):
            row["warnings"] = json.loads(row.get("warnings") or "[]")
            if row.get("personalization_score") not in (None, ""):
                row["personalization_score"] = int(row["personalization_score"])
            drafts.append(EmailDraft(**row))
        return drafts
