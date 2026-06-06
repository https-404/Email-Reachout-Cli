from jobreach.core.models import CandidateProfile, EmailDraft, Lead
from jobreach.safety.quality import check_email_quality


def test_quality_flags_invented_context():
    profile = CandidateProfile(
        candidate_title="Developer",
        seniority="Junior",
        target_roles=["Developer"],
        skills=["Python"],
        projects=["Automation"],
        experience_summary="Summary",
        best_pitch="Pitch",
    )
    draft = EmailDraft(
        id="1",
        email="hr@example.com",
        recipient_type="hr",
        subject="Hello",
        body="I noticed your recent hiring. I work with Python. Would you be open to chat?",
    )
    checked = check_email_quality(draft, profile, Lead(email="hr@example.com"))
    assert checked.risk == "high"
    assert checked.personalization_score < 8
