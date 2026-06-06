import csv
from pathlib import Path


def load_do_not_contact(path: str | Path) -> set[str]:
    source = Path(path)
    if not source.exists():
        return set()
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames and "email" in reader.fieldnames:
            return {row.get("email", "").strip().lower() for row in reader if row.get("email")}
        handle.seek(0)
        return {line.strip().lower() for line in handle if line.strip() and line.strip().lower() != "email"}
