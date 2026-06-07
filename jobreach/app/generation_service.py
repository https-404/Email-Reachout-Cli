import uuid

from jobreach.ai.base import AIClient
from jobreach.ai.evaluator import AIQualityEvaluator
from jobreach.ai.generator import generate_email
from jobreach.core.models import CandidateProfile, EmailDraft, Lead
from jobreach.safety.quality import check_email_quality


class GenerationService:
    def __init__(self, ai_client: AIClient, review_client: AIClient | None = None):
        self.ai_client = ai_client
        self.review_client = review_client

    def generate_drafts(
        self,
        profile: CandidateProfile,
        leads: list[Lead],
        ai_quality_check: bool = False,
        tone_preset: str = "default",
    ) -> list[EmailDraft]:
        drafts: list[EmailDraft] = []
        evaluator = AIQualityEvaluator(self.review_client or self.ai_client) if ai_quality_check else None
        for lead in leads:
            try:
                generated = generate_email(self.ai_client, profile, lead, tone_preset=tone_preset)
                draft = EmailDraft(
                    id=str(uuid.uuid4()),
                    email=lead.email,
                    company=lead.company,
                    recipient_name=lead.recipient_name,
                    recipient_type=lead.recipient_type or "unknown",
                    subject=generated.subject,
                    body=generated.body,
                    alt_subject=generated.alt_subject,
                    provider=self.ai_client.provider,
                    model=self.ai_client.model_name,
                )
                draft = check_email_quality(draft, profile, lead)
                if evaluator:
                    evaluation = evaluator.evaluate(profile, lead, draft)
                    draft.personalization_score = evaluation.personalization_score
                    draft.risk = evaluation.risk
                    draft.warnings = evaluation.warnings
                    draft.quality_reason = evaluation.reason
                drafts.append(draft)
            except Exception as exc:
                drafts.append(
                    EmailDraft(
                        id=str(uuid.uuid4()),
                        email=lead.email,
                        company=lead.company,
                        recipient_name=lead.recipient_name,
                        recipient_type=lead.recipient_type or "unknown",
                        subject="",
                        body="",
                        risk="high",
                        warnings=["generation failed"],
                        status="failed",
                        error=str(exc),
                        provider=self.ai_client.provider,
                        model=self.ai_client.model_name,
                    )
                )
        return drafts

    def regenerate_draft(
        self,
        profile: CandidateProfile,
        lead: Lead,
        tone_preset: str = "default",
        ai_quality_check: bool = False,
    ) -> EmailDraft:
        drafts = self.generate_drafts(profile, [lead], ai_quality_check=ai_quality_check, tone_preset=tone_preset)
        return drafts[0]
