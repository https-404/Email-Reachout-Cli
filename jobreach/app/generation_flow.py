from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jobreach.ai.factory import AIClientFactory
from jobreach.app.profile_service import ProfileService, save_profile
from jobreach.app.generation_service import GenerationService
from jobreach.config.paths import drafts_dir, profiles_dir
from jobreach.config.settings import SettingsStore
from jobreach.drafts.index import add_batch
from jobreach.drafts.store import save_drafts
from jobreach.leads.loader import load_leads_csv


@dataclass
class GenerationSummary:
    generated: int
    high_risk: int
    failed: int
    output_path: str
    batch_id: str


def run_shell_generation(
    cv_path: str,
    leads_path: str,
    limit: int | None,
    settings_store: SettingsStore,
    secret_store,
) -> GenerationSummary:
    settings = settings_store.load()
    ai_client = AIClientFactory.from_settings(settings, secret_store)
    profile = ProfileService(ai_client).create_profile_from_cv(cv_path)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    profile_out = profiles_dir() / f"profile_{timestamp}.json"
    save_profile(profile, str(profile_out))

    leads = load_leads_csv(leads_path)
    if limit is not None:
        leads = leads[:limit]

    drafts = GenerationService(ai_client).generate_drafts(profile, leads)
    batch_id = f"drafts_{timestamp}"
    output_path = drafts_dir() / f"{batch_id}.csv"
    save_drafts(str(output_path), drafts)

    add_batch(
        batch_id=batch_id,
        path=str(output_path),
        count=len(drafts),
        provider=settings.default_provider or "",
        model=settings.default_model or "",
    )

    high_risk = sum(1 for draft in drafts if draft.risk == "high")
    failed = sum(1 for draft in drafts if draft.status == "failed")
    return GenerationSummary(
        generated=len(drafts),
        high_risk=high_risk,
        failed=failed,
        output_path=str(output_path),
        batch_id=batch_id,
    )
