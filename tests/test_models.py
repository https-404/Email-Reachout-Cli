from jobreach.core.models import CandidateProfile, Lead


def test_models_validation():
    profile = CandidateProfile(
        candidate_title="Developer",
        seniority="Junior",
        target_roles=["Backend Developer"],
        skills=["Python"],
        projects=["CLI"],
        experience_summary="Builds tools.",
        best_pitch="Useful developer.",
    )
    lead = Lead(email="hr@example.com")
    assert profile.candidate_title == "Developer"
    assert str(lead.email) == "hr@example.com"
