from jobreach.app.campaign_service import CampaignService
from jobreach.config.settings import SettingsStore


def test_campaign_service_dnc(tmp_path):
    service = CampaignService(SettingsStore(path=tmp_path / "settings.json"))
    cid = service.create_campaign("Q1 outreach")
    assert cid
    service.add_dnc("blocked@example.com")
    assert "blocked@example.com" in service.list_dnc()
    assert service.remove_dnc("blocked@example.com")
