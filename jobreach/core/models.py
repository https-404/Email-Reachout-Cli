from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class CandidateProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    candidate_title: str = Field(..., description="Short title, e.g. Full-stack Developer")
    seniority: str = Field(..., description="Intern, Junior, Mid-level, Senior")
    target_roles: list[str]
    skills: list[str]
    projects: list[str]
    experience_summary: str
    best_pitch: str
    preferred_tone: str = "confident, concise, friendly"


class Lead(BaseModel):
    email: EmailStr
    company: Optional[str] = None
    recipient_name: Optional[str] = None
    website: Optional[str] = None
    role: Optional[str] = None
    job_url: Optional[str] = None
    notes: Optional[str] = None
    recipient_type: Optional[str] = None


class EmailDraft(BaseModel):
    id: str
    email: EmailStr
    company: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_type: str
    subject: str
    body: str
    personalization_score: int = 0
    risk: Literal["low", "medium", "high"] = "medium"
    warnings: list[str] = Field(default_factory=list)
    status: Literal["draft", "approved", "sent", "skipped", "failed"] = "draft"
    sent_at: Optional[str] = None
    error: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class SendResult(BaseModel):
    draft_id: str
    email: EmailStr
    status: Literal["sent", "skipped", "failed"]
    reason: Optional[str] = None
    gmail_message_id: Optional[str] = None


class AIProviderConfig(BaseModel):
    provider: Literal["gemini", "openai", "anthropic"]
    model: str
    temperature: float = 0.4
    max_tokens: int = 1200
