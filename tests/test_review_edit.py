from jobreach.core.models import CandidateProfile, EmailDraft, Lead
from jobreach.app.review_service import interactive_review


def test_interactive_review_edit_subject(tmp_path, monkeypatch):
    batch_path = tmp_path / "drafts.csv"
    draft = EmailDraft(
        id="d1",
        email="hr@acme.com",
        company="Acme",
        recipient_type="hr",
        subject="Old subject",
        body="Hello body",
        personalization_score=7,
        risk="low",
    )
    from jobreach.drafts.store import save_drafts

    save_drafts(str(batch_path), [draft])

    choices = iter([3, 8])
    monkeypatch.setattr("jobreach.app.review_service.choose_menu_option", lambda *a, **k: next(choices))
    monkeypatch.setattr("jobreach.app.review_service.prompt_text", lambda msg, default="": "New subject")

    interactive_review(str(batch_path), "batch1", start_index=0)
    from jobreach.drafts.store import load_drafts

    updated = load_drafts(str(batch_path))[0]
    assert updated.subject == "New subject"
    assert updated.edited_at is not None
