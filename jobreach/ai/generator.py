from jobreach.ai.base import AIClient
from jobreach.ai.prompt_builder import build_email_prompt
from jobreach.ai.schemas import GeneratedEmailSchema
from jobreach.core.models import CandidateProfile, Lead


def generate_email(ai_client: AIClient, profile: CandidateProfile, lead: Lead) -> GeneratedEmailSchema:
    return ai_client.generate_structured(build_email_prompt(profile, lead), GeneratedEmailSchema)
