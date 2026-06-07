from typing import Type, TypeVar

from pydantic import BaseModel

from jobreach.ai.base import AIClient
from jobreach.ai.schemas import GeneratedEmailSchema
from jobreach.core.models import CandidateProfile

T = TypeVar("T", bound=BaseModel)


class DemoAIClient(AIClient):
    """Mock AI client for onboarding without API spend."""

    def generate_text(self, prompt: str) -> str:
        return "Demo profile text."

    def generate_structured(self, prompt: str, schema: Type[T]) -> T:
        if schema is GeneratedEmailSchema:
            return schema(
                subject="Quick intro — demo draft",
                body=(
                    "Hi,\n\n"
                    "I'm exploring roles where I can contribute with Python and product engineering. "
                    "Would you be open to a brief chat about opportunities on your team?\n\n"
                    "Best,\nDemo Candidate"
                ),
                alt_subject="Following up on opportunities",
            )
        if schema is CandidateProfile:
            return CandidateProfile(
                candidate_title="Software Engineer",
                seniority="Mid-level",
                target_roles=["Software Engineer", "Backend Developer"],
                skills=["Python", "FastAPI", "React"],
                projects=["CLI outreach tool"],
                experience_summary="Built automation and outreach demos.",
                best_pitch="Practical engineer who ships CLI tools quickly.",
            )
        if hasattr(schema, "model_fields"):
            defaults = {name: "Demo" for name in schema.model_fields}
            return schema(**defaults)
        raise NotImplementedError(f"Demo client does not support schema: {schema}")
