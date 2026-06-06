from jobreach.drafts.index import add_batch, list_batches, update_batch_stats
from jobreach.drafts.store import save_drafts
from jobreach.core.models import EmailDraft


def test_draft_index_tracks_approved(tmp_path, monkeypatch):
    drafts_path = tmp_path / "drafts_test.csv"
    index_path = tmp_path / "index.json"
    monkeypatch.setattr("jobreach.drafts.index.drafts_index_path", lambda: index_path)

    save_drafts(
        str(drafts_path),
        [
            EmailDraft(
                id="1",
                email="a@example.com",
                recipient_type="unknown",
                subject="S",
                body="B",
                status="approved",
            )
        ],
    )
    add_batch("drafts_test", str(drafts_path), 1, "openai", "gpt-4o-mini")
    update_batch_stats("drafts_test")
    batches = list_batches()
    assert len(batches) == 1
    assert batches[0].approved == 1
