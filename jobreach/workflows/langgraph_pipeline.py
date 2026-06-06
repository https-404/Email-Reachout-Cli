from typing import TypedDict

from jobreach.core.models import CandidateProfile, EmailDraft, Lead


class OutreachState(TypedDict):
    cv_text: str
    profile: CandidateProfile | None
    leads: list[Lead]
    drafts: list[EmailDraft]
    current_index: int
    errors: list[str]


def build_langgraph_pipeline():
    raise NotImplementedError("LangGraph workflow is deferred until the simple pipeline needs it.")
