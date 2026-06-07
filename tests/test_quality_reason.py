from jobreach.safety.quality import check_email_quality
from jobreach.core.models import CandidateProfile, EmailDraft, Lead


def test_quality_reason_set():
    profile = CandidateProfile(
        candidate_title="Engineer",
        seniority="Mid",
        target_roles=["Engineer"],
        skills=["Python"],
        projects=["App"],
        experience_summary="Built apps",
        best_pitch="Ships fast",
    )
    draft = EmailDraft(
        id="1",
        email="a@b.com",
        company="Co",
        recipient_type="hr",
        subject="",
        body="",
        personalization_score=1,
        risk="high",
    )
    result = check_email_quality(draft, profile, Lead(email="a@b.com"))
    assert result.quality_reason is not None
    assert "Score" in result.quality_reason
