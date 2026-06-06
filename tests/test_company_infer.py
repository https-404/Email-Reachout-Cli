from jobreach.leads.company_infer import infer_company_from_email


def test_infer_company_from_email():
    assert infer_company_from_email("hr@acme.ai") == "Acme"
    assert infer_company_from_email("careers@nova-tech.com") == "Nova Tech"
    assert infer_company_from_email("jobs@company.co.uk") == "Company"
