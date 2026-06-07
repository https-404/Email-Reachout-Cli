from typing import Literal

from pydantic import BaseModel

from jobreach.core.models import CandidateProfile

CandidateProfileSchema = CandidateProfile


class GeneratedEmailSchema(BaseModel):
    subject: str
    body: str
    alt_subject: str | None = None


class QualityEvaluationSchema(BaseModel):
    personalization_score: int
    risk: Literal["low", "medium", "high"]
    warnings: list[str]
    reason: str
