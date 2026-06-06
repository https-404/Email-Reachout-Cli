from jobreach.ai.prompt_builder import build_email_prompt
from jobreach.core.models import CandidateProfile, Lead


def test_prompt_contains_safety_rules():
    profile = CandidateProfile(
        candidate_title="Developer",
        seniority="Junior",
        target_roles=["Developer"],
        skills=["Python"],
        projects=["Automation"],
        experience_summary="Summary",
        best_pitch="Pitch",
    )
    prompt = build_email_prompt(profile, Lead(email="hr@example.com", recipient_type="hr"))
    assert "Do not invent company facts" in prompt
    assert "Do not claim there is a job opening" in prompt
