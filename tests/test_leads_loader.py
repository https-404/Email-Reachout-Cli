from jobreach.leads.loader import load_leads_csv


def test_load_leads_skips_invalid_and_dedupes(tmp_path):
    path = tmp_path / "leads.csv"
    path.write_text("email,company\nhr@acme.ai,\ninvalid,\nhr@acme.ai,\n", encoding="utf-8")
    leads = load_leads_csv(str(path))
    assert len(leads) == 1
    assert leads[0].company == "Acme"
    assert leads[0].recipient_type == "hr"
