from jobreach.storage.sqlite_store import SQLiteStore


def test_send_queue(tmp_path, monkeypatch):
    monkeypatch.setattr("jobreach.storage.sqlite_store.crm_db_path", lambda: tmp_path / "crm.db")
    store = SQLiteStore()
    store.queue_draft("d1", "/batch.csv", "a@b.com", "2026-01-01T09:00:00+00:00")
    queued = store.list_queue()
    assert len(queued) == 1
    store.mark_queue_sent(queued[0]["id"])
    assert store.list_queue() == []
