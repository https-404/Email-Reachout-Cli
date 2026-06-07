import csv
from pathlib import Path

from jobreach.config.paths import sent_log_path
from jobreach.utils.files import ensure_parent
from jobreach.utils.time import utc_now_iso

FIELDS = ["email", "subject", "sent_at", "draft_id", "gmail_message_id"]


class SentLog:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else sent_log_path()
        ensure_parent(self.path)
        if not self.path.exists():
            with self.path.open("w", encoding="utf-8", newline="") as handle:
                csv.DictWriter(handle, fieldnames=FIELDS).writeheader()

    def _rows(self) -> list[dict[str, str]]:
        with self.path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def has_been_sent(self, email: str, subject: str) -> bool:
        key = (email.lower(), subject.strip().lower())
        return any((row["email"].lower(), row["subject"].strip().lower()) == key for row in self._rows())

    def record_sent(self, email: str, subject: str, draft_id: str, gmail_message_id: str) -> None:
        with self.path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writerow(
                {
                    "email": email,
                    "subject": subject,
                    "sent_at": utc_now_iso(),
                    "draft_id": draft_id,
                    "gmail_message_id": gmail_message_id,
                }
            )

    def count_sent(self) -> int:
        rows = self._rows()
        return len(rows)

    def read_all(self) -> list[dict[str, str]]:
        return self._rows()
