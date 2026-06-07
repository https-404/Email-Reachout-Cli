import json

from jobreach.drafts.index import add_batch, get_batch, list_batches, update_batch_review_index


def test_resume_review_index_persisted(tmp_path, monkeypatch):
    monkeypatch.setattr("jobreach.drafts.index.drafts_index_path", lambda: tmp_path / "index.json")
    add_batch("b1", "/tmp/d.csv", 10, "openai", "gpt-4o-mini")
    update_batch_review_index("b1", 5)
    batch = get_batch("b1")
    assert batch is not None
    assert batch.last_review_index == 5
