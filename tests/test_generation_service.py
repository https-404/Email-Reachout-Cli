from typing import Type, TypeVar

from pydantic import BaseModel

from jobreach.ai.base import AIClient
from jobreach.ai.schemas import GeneratedEmailSchema
from jobreach.app.generation_service import GenerationService
from jobreach.core.models import CandidateProfile, Lead

T = TypeVar("T", bound=BaseModel)


class FakeAIClient(AIClient):
    provider = "fake"
    model_name = "fake-model"

    def generate_text(self, prompt: str) -> str:
        return "text"

    def generate_structured(self, prompt: str, schema: Type[T]) -> T:
        return schema(subject="Hello", body="I work with Python. Would you be open to chat?")


def test_generation_service_creates_drafts():
    profile = CandidateProfile(
        candidate_title="Developer",
        seniority="Junior",
        target_roles=["Developer"],
        skills=["Python"],
        projects=["Automation"],
        experience_summary="Summary",
        best_pitch="Pitch",
    )
    drafts = GenerationService(FakeAIClient()).generate_drafts(profile, [Lead(email="hr@example.com", recipient_type="hr")])
    assert len(drafts) == 1
    assert drafts[0].provider == "fake"
    assert drafts[0].subject == "Hello"
