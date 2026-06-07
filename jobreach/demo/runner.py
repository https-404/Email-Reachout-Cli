from datetime import datetime
from importlib import resources
from pathlib import Path

from jobreach.app.generation_service import GenerationService
from jobreach.app.profile_service import ProfileService, save_profile
from jobreach.config.paths import drafts_dir, profiles_dir
from jobreach.config.settings import SettingsStore
from jobreach.demo.mock_ai import DemoAIClient
from jobreach.drafts.index import add_batch
from jobreach.drafts.store import save_drafts
from jobreach.leads.preview import load_leads_with_stats
from jobreach.logs.run_log import record_run


def _fixture_path(name: str) -> Path:
    with resources.as_file(resources.files("jobreach.demo.fixtures") / name) as path:
        return Path(path)


def run_demo_generation(settings_store: SettingsStore | None = None) -> str:
    settings_store = settings_store or SettingsStore()
    ai = DemoAIClient()
    cv_path = _fixture_path("sample_cv.txt")
    leads_path = _fixture_path("sample_leads.csv")

    profile = ProfileService(ai).create_profile_from_cv(str(cv_path))
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    profile_out = profiles_dir() / f"demo_profile_{timestamp}.json"
    save_profile(profile, str(profile_out))

    leads, stats = load_leads_with_stats(str(leads_path))
    drafts = GenerationService(ai).generate_drafts(profile, leads, ai_quality_check=False, tone_preset="default")
    batch_id = f"demo_{timestamp}"
    output_path = drafts_dir() / f"{batch_id}.csv"
    save_drafts(str(output_path), drafts)
    add_batch(
        batch_id=batch_id,
        path=str(output_path),
        count=len(drafts),
        provider="demo",
        model="mock",
        profile_path=str(profile_out),
    )
    settings_store.update(last_cv_path=str(cv_path), last_leads_path=str(leads_path))
    record_run("demo_generate", {"batch_id": batch_id, "generated": len(drafts), "invalid_skipped": stats.invalid_skipped})
    return str(output_path)
