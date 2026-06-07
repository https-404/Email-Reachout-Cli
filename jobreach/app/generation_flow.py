from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from jobreach.ai.factory import AIClientFactory
from jobreach.app.generation_service import GenerationService
from jobreach.app.profile_service import ProfileService, save_profile
from jobreach.config.paths import drafts_dir, profiles_dir
from jobreach.config.settings import SettingsStore
from jobreach.drafts.index import add_batch
from jobreach.drafts.store import save_drafts
from jobreach.leads.enrichment import enrich_leads
from jobreach.leads.preview import load_leads_with_stats
from jobreach.logs.run_log import record_run


@dataclass
class GenerationSummary:
    generated: int
    high_risk: int
    failed: int
    medium_risk: int = 0
    low_risk: int = 0
    by_recipient_type: dict[str, int] = field(default_factory=dict)
    output_path: str = ""
    batch_id: str = ""
    profile_path: str = ""


def run_shell_generation(
    cv_path: str,
    leads_path: str,
    limit: int | None,
    settings_store: SettingsStore,
    secret_store,
    campaign_id: str | None = None,
) -> GenerationSummary:
    settings = settings_store.load()
    generate_model = settings.generate_model or settings.default_model
    review_model = settings.review_model or settings.default_model

    gen_settings = settings.model_copy(update={"default_model": generate_model})
    ai_client = AIClientFactory.from_settings(gen_settings, secret_store)
    review_client = None
    if settings.ai_quality_check and review_model != generate_model:
        review_settings = settings.model_copy(update={"default_model": review_model})
        review_client = AIClientFactory.from_settings(review_settings, secret_store)

    profile = ProfileService(ai_client).create_profile_from_cv(cv_path)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    profile_out = profiles_dir() / f"profile_{timestamp}.json"
    save_profile(profile, str(profile_out))

    leads, stats = load_leads_with_stats(leads_path)
    if settings.enrichment_enabled:
        leads = enrich_leads(leads)
    if limit is not None:
        leads = leads[:limit]

    drafts = GenerationService(ai_client, review_client).generate_drafts(
        profile,
        leads,
        ai_quality_check=settings.ai_quality_check,
        tone_preset=settings.tone_preset,
    )
    batch_id = f"drafts_{timestamp}"
    output_path = drafts_dir() / f"{batch_id}.csv"
    save_drafts(str(output_path), drafts)
    add_batch(
        batch_id=batch_id,
        path=str(output_path),
        count=len(drafts),
        provider=settings.default_provider or "",
        model=generate_model or "",
        campaign_id=campaign_id,
    )

    settings_store.update(last_cv_path=cv_path, last_leads_path=leads_path)

    by_type: dict[str, int] = {}
    for draft in drafts:
        by_type[draft.recipient_type] = by_type.get(draft.recipient_type, 0) + 1

    summary = GenerationSummary(
        generated=len(drafts),
        high_risk=sum(1 for d in drafts if d.risk == "high"),
        medium_risk=sum(1 for d in drafts if d.risk == "medium"),
        low_risk=sum(1 for d in drafts if d.risk == "low"),
        failed=sum(1 for d in drafts if d.status == "failed"),
        by_recipient_type=by_type,
        output_path=str(output_path),
        batch_id=batch_id,
        profile_path=str(profile_out),
    )
    record_run(
        "generate",
        {
            "batch_id": batch_id,
            "generated": summary.generated,
            "invalid_skipped": stats.invalid_skipped,
            "duplicates_skipped": stats.duplicates_skipped,
        },
    )
    return summary
