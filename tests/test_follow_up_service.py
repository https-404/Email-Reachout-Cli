from jobreach.app.follow_up_service import FollowUpService
from jobreach.config.settings import SettingsStore


class _Secrets:
    def get_provider_key(self, provider):
        return "test-key"


def test_follow_up_no_candidates(tmp_path):
    service = FollowUpService(SettingsStore(path=tmp_path / "settings.json"), _Secrets())
    assert service.candidates_for_follow_up() == []
    assert service.create_follow_up_batch() is None
