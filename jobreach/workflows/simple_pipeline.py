from jobreach.ai.base import AIClient
from jobreach.app.generation_service import GenerationService
from jobreach.app.profile_service import ProfileService, load_profile
from jobreach.core.models import EmailDraft
from jobreach.drafts.store import save_drafts
from jobreach.leads.loader import load_leads_csv


def run_generation_pipeline(
    cv_path: str | None,
    profile_path: str | None,
    leads_path: str,
    out_path: str,
    ai_client: AIClient,
    ai_quality_check: bool = False,
    max_leads: int | None = None,
) -> list[EmailDraft]:
    if profile_path:
        profile = load_profile(profile_path)
    elif cv_path:
        profile = ProfileService(ai_client).create_profile_from_cv(cv_path)
    else:
        raise ValueError("Either cv_path or profile_path is required")
    leads = load_leads_csv(leads_path)
    if max_leads is not None:
        leads = leads[:max_leads]
    drafts = GenerationService(ai_client).generate_drafts(profile, leads, ai_quality_check=ai_quality_check)
    save_drafts(out_path, drafts)
    return drafts
