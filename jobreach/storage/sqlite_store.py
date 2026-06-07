import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from jobreach.config.paths import crm_db_path, ensure_data_dirs


class SQLiteStore:
    def __init__(self, path: Path | None = None):
        ensure_data_dirs()
        self.path = path or crm_db_path()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    cv_path TEXT,
                    leads_path TEXT,
                    tone TEXT,
                    provider TEXT,
                    model TEXT
                );
                CREATE TABLE IF NOT EXISTS contacts (
                    email TEXT PRIMARY KEY,
                    company TEXT,
                    reply_status TEXT DEFAULT 'none',
                    last_contacted_at TEXT
                );
                CREATE TABLE IF NOT EXISTS send_events (
                    id TEXT PRIMARY KEY,
                    draft_id TEXT,
                    email TEXT,
                    subject TEXT,
                    sent_at TEXT,
                    gmail_message_id TEXT,
                    campaign_id TEXT
                );
                CREATE TABLE IF NOT EXISTS send_queue (
                    id TEXT PRIMARY KEY,
                    draft_id TEXT,
                    batch_path TEXT,
                    email TEXT,
                    scheduled_at TEXT,
                    status TEXT DEFAULT 'queued'
                );
                """
            )

    def create_campaign(
        self,
        name: str,
        cv_path: str | None = None,
        leads_path: str | None = None,
        tone: str = "default",
        provider: str = "",
        model: str = "",
    ) -> str:
        campaign_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO campaigns (id, name, created_at, cv_path, leads_path, tone, provider, model) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    campaign_id,
                    name,
                    datetime.now(timezone.utc).isoformat(),
                    cv_path,
                    leads_path,
                    tone,
                    provider,
                    model,
                ),
            )
        return campaign_id

    def list_campaigns(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM campaigns ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]

    def upsert_contact(self, email: str, company: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO contacts (email, company) VALUES (?, ?) "
                "ON CONFLICT(email) DO UPDATE SET company=excluded.company",
                (email.lower(), company),
            )

    def mark_replied(self, email: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO contacts (email, reply_status) VALUES (?, 'replied') "
                "ON CONFLICT(email) DO UPDATE SET reply_status='replied'",
                (email.lower(),),
            )

    def get_contact(self, email: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM contacts WHERE email=?", (email.lower(),)).fetchone()
        return dict(row) if row else None

    def record_send_event(
        self,
        draft_id: str,
        email: str,
        subject: str,
        gmail_message_id: str,
        campaign_id: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO send_events (id, draft_id, email, subject, sent_at, gmail_message_id, campaign_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    draft_id,
                    email.lower(),
                    subject,
                    datetime.now(timezone.utc).isoformat(),
                    gmail_message_id,
                    campaign_id,
                ),
            )
            conn.execute(
                "INSERT INTO contacts (email, reply_status, last_contacted_at) VALUES (?, 'no_reply', ?) "
                "ON CONFLICT(email) DO UPDATE SET last_contacted_at=excluded.last_contacted_at",
                (email.lower(), datetime.now(timezone.utc).isoformat()),
            )

    def queue_draft(self, draft_id: str, batch_path: str, email: str, scheduled_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO send_queue (id, draft_id, batch_path, email, scheduled_at, status) VALUES (?, ?, ?, ?, ?, 'queued')",
                (str(uuid.uuid4()), draft_id, batch_path, email.lower(), scheduled_at),
            )

    def list_queue(self, status: str = "queued") -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM send_queue WHERE status=? ORDER BY scheduled_at",
                (status,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_replied_emails(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT email FROM contacts WHERE reply_status='replied'").fetchall()
        return [row["email"] for row in rows]

    def mark_queue_sent(self, queue_id: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE send_queue SET status='sent' WHERE id=?", (queue_id,))
