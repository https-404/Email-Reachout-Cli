from jobreach.leads.enrichment import enrich_leads
from jobreach.core.models import Lead


def test_enrich_leads_no_website_unchanged():
    leads = [Lead(email="a@b.com", company="Co")]
    result = enrich_leads(leads)
    assert len(result) == 1
    assert result[0].company == "Co"
