from jobreach.ai.base import AIClient
from jobreach.ai.prompt_builder import build_quality_prompt
from jobreach.ai.schemas import QualityEvaluationSchema
from jobreach.core.models import CandidateProfile, EmailDraft, Lead


class AIQualityEvaluator:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def evaluate(self, profile: CandidateProfile, lead: Lead, draft: EmailDraft) -> QualityEvaluationSchema:
        return self.ai_client.generate_structured(build_quality_prompt(profile, lead, draft), QualityEvaluationSchema)
