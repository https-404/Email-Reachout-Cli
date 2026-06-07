from jobreach.app.generation_flow import GenerationSummary


def test_generation_summary_fields():
    summary = GenerationSummary(
        generated=5,
        high_risk=1,
        failed=0,
        medium_risk=2,
        low_risk=2,
        by_recipient_type={"hr": 3, "unknown": 2},
        output_path="/tmp/x.csv",
        batch_id="b1",
        profile_path="/tmp/p.json",
    )
    assert summary.profile_path.endswith(".json")
    assert summary.by_recipient_type["hr"] == 3
