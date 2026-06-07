from jobreach.leads.preview import load_leads_with_stats


def test_load_leads_with_stats(tmp_path):
    csv_path = tmp_path / "leads.csv"
    csv_path.write_text("email,company\nhr@acme.com,Acme\nbad,\nhr@acme.com,Acme\n", encoding="utf-8")
    leads, stats = load_leads_with_stats(str(csv_path))
    assert stats.valid == 1
    assert stats.duplicates_skipped >= 1
