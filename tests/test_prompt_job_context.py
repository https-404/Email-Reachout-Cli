from jobreach.ai.prompt_builder import build_email_prompt
from jobreach.core.models import CandidateProfile, Lead


def test_prompt_includes_job_url_and_notes():
    profile = CandidateProfile(
        candidate_title="Engineer",
        seniority="Mid",
        target_roles=["Engineer"],
        skills=["Python"],
        projects=["App"],
        experience_summary="Built apps",
        best_pitch="Ships fast",
    )
    lead = Lead(
        email="hr@co.com",
        company="Co",
        job_url="https://jobs.example.com/123",
        notes="Hiring backend engineers",
        role="Backend Engineer",
    )
    prompt = build_email_prompt(profile, lead, tone_preset="default")
    assert "https://jobs.example.com/123" in prompt
    assert "Hiring backend engineers" in prompt
    assert "Backend Engineer" in prompt
