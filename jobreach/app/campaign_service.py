from jobreach.config.paths import do_not_contact_path
from jobreach.config.settings import SettingsStore
from jobreach.storage.sqlite_store import SQLiteStore


class CampaignService:
    def __init__(self, settings_store: SettingsStore | None = None):
        self.settings = settings_store or SettingsStore()
        self.db = SQLiteStore()

    def create_campaign(self, name: str, cv_path: str | None = None, leads_path: str | None = None) -> str:
        settings = self.settings.load()
        return self.db.create_campaign(
            name=name,
            cv_path=cv_path,
            leads_path=leads_path,
            tone=settings.tone_preset,
            provider=settings.default_provider or "",
            model=settings.default_model or "",
        )

    def list_campaigns(self) -> list[dict]:
        return self.db.list_campaigns()

    def mark_replied(self, email: str, add_to_dnc: bool = False) -> None:
        self.db.mark_replied(email)
        if add_to_dnc:
            self.add_dnc(email)

    def add_dnc(self, email: str) -> None:
        path = do_not_contact_path()
        existing = set()
        if path.exists():
            existing = {line.strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
        email = email.lower()
        if email not in existing:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(f"{email}\n")

    def remove_dnc(self, email: str) -> bool:
        path = do_not_contact_path()
        if not path.exists():
            return False
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip().lower() != email.lower()]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return True

    def list_dnc(self) -> list[str]:
        path = do_not_contact_path()
        if not path.exists():
            return []
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and line.strip() != "email"]
