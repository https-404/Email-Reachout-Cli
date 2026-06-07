import json

from jinja2 import Template

from jobreach.ai.tone_presets import get_tone_preset
from jobreach.ai.prompts import EMAIL_GENERATION_PROMPT, PROFILE_EXTRACTION_PROMPT, QUALITY_EVALUATION_PROMPT
from jobreach.core.constants import RECIPIENT_INSTRUCTIONS
from jobreach.core.models import CandidateProfile, EmailDraft, Lead


def _model_json(model) -> str:
    return json.dumps(model.model_dump(mode="json"), indent=2)


def build_profile_prompt(cv_text: str) -> str:
    return Template(PROFILE_EXTRACTION_PROMPT).render(cv_text=cv_text)


def build_email_prompt(profile: CandidateProfile, lead: Lead, tone_preset: str = "default") -> str:
    recipient_type = lead.recipient_type or "unknown"
    tone = get_tone_preset(tone_preset)
    profile_data = profile.model_copy(update={"preferred_tone": tone["preferred_tone"]})
    return Template(EMAIL_GENERATION_PROMPT).render(
        profile_json=_model_json(profile_data),
        lead_json=_model_json(lead),
        recipient_type=recipient_type,
        recipient_instruction=RECIPIENT_INSTRUCTIONS.get(recipient_type, RECIPIENT_INSTRUCTIONS["unknown"]),
        tone_instruction=tone["instruction"],
        job_url=lead.job_url or "",
        role=lead.role or "",
        notes=lead.notes or "",
    )


def build_quality_prompt(profile: CandidateProfile, lead: Lead, draft: EmailDraft) -> str:
    return Template(QUALITY_EVALUATION_PROMPT).render(
        profile_json=_model_json(profile),
        lead_json=_model_json(lead),
        draft_json=_model_json(draft),
    )
