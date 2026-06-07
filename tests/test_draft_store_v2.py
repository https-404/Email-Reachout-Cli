from jobreach.drafts.store import load_drafts, save_drafts
from jobreach.core.models import EmailDraft


def test_draft_csv_backward_compat(tmp_path):
    legacy = "id,email,company,recipient_name,recipient_type,subject,body,personalization_score,risk,warnings,status,sent_at,error,provider,model\n"
    legacy += '1,a@b.com,Co,,hr,Hi,Body,8,low,[],draft,,,openai,gpt-4o-mini\n'
    path = tmp_path / "legacy.csv"
    path.write_text(legacy, encoding="utf-8")
    drafts = load_drafts(str(path))
    assert drafts[0].reply_status == "none"
    assert drafts[0].alt_subject is None

    save_drafts(str(path), drafts)
    reloaded = load_drafts(str(path))
    assert reloaded[0].email == "a@b.com"
