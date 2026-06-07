from jobreach.storage.sqlite_store import SQLiteStore


def test_sqlite_crm_campaign_and_contact(tmp_path, monkeypatch):
    db_path = tmp_path / "crm.db"
    monkeypatch.setattr("jobreach.storage.sqlite_store.crm_db_path", lambda: db_path)
    store = SQLiteStore()
    cid = store.create_campaign("Test", cv_path="/cv.pdf", leads_path="/leads.csv")
    campaigns = store.list_campaigns()
    assert len(campaigns) == 1
    assert campaigns[0]["name"] == "Test"
    store.mark_replied("user@example.com")
    contact = store.get_contact("user@example.com")
    assert contact["reply_status"] == "replied"
