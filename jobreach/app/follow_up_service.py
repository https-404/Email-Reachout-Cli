from datetime import datetime, timedelta, timezone

from jobreach.ai.factory import AIClientFactory
from jobreach.app.generation_service import GenerationService
from jobreach.app.profile_service import load_profile
from jobreach.config.paths import drafts_dir
from jobreach.config.settings import SettingsStore
from jobreach.core.models import Lead
from jobreach.drafts.index import add_batch
from jobreach.drafts.store import save_drafts
from jobreach.logs.sent_log import SentLog
from jobreach.storage.sqlite_store import SQLiteStore


class FollowUpService:
    def __init__(self, settings_store: SettingsStore, secret_store):
        self.settings_store = settings_store
        self.secret_store = secret_store
        self.db = SQLiteStore()

    def candidates_for_follow_up(self, days: int | None = None) -> list[dict]:
        settings = self.settings_store.load()
        days = days or settings.follow_up_days
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        sent_log = SentLog()
        results = []
        for row in sent_log._rows():
            sent_at = row.get("sent_at", "")
            try:
                sent_dt = datetime.fromisoformat(sent_at.replace("Z", "+00:00"))
            except ValueError:
                continue
            if sent_dt > cutoff:
                continue
            email = row["email"].lower()
            contact = self.db.get_contact(email)
            if contact and contact.get("reply_status") == "replied":
                continue
            results.append(row)
        return results

    def create_follow_up_batch(self) -> str | None:
        settings = self.settings_store.load()
        candidates = self.candidates_for_follow_up()
        if not candidates:
            return None

        ai_client = AIClientFactory.from_settings(settings, self.secret_store)
        gen = GenerationService(ai_client)
        profiles = list(profiles_dir().glob("profile_*.json")) if (profiles_dir := drafts_dir().parent / "profiles") else []
        if not profiles:
            return None
        profile = load_profile(str(sorted(profiles)[-1]))

        follow_up_drafts = []
        for row in candidates:
            lead = Lead(email=row["email"], company=None, recipient_type="unknown")
            draft = gen.regenerate_draft(profile, lead, tone_preset=settings.tone_preset)
            draft.follow_up_of = row.get("draft_id")
            draft.subject = f"Re: {row['subject']}" if not draft.subject.lower().startswith("re:") else draft.subject
            follow_up_drafts.append(draft)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        new_id = f"followup_{timestamp}"
        out_path = drafts_dir() / f"{new_id}.csv"
        save_drafts(str(out_path), follow_up_drafts)
        add_batch(new_id, str(out_path), len(follow_up_drafts), settings.default_provider or "", settings.default_model or "")
        return str(out_path)
