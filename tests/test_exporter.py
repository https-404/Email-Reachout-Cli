from jobreach.drafts.exporter import export_campaign_report


def test_export_campaign_report(tmp_path):
    path = export_campaign_report("test-report", tmp_path)
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "JobReach Campaign Report" in text
