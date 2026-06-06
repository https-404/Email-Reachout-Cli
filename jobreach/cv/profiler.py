from jobreach.ai.base import AIClient
from jobreach.ai.prompt_builder import build_profile_prompt
from jobreach.core.models import CandidateProfile


def extract_profile(cv_text: str, ai_client: AIClient) -> CandidateProfile:
    return ai_client.generate_structured(build_profile_prompt(cv_text), CandidateProfile)
