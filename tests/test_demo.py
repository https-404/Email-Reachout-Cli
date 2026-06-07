from jobreach.demo.runner import run_demo_generation


def test_demo_generation_creates_batch(tmp_path, monkeypatch):
    monkeypatch.setattr("jobreach.demo.runner.drafts_dir", lambda: tmp_path / "drafts")
    monkeypatch.setattr("jobreach.demo.runner.profiles_dir", lambda: tmp_path / "profiles")
    (tmp_path / "drafts").mkdir()
    (tmp_path / "profiles").mkdir()
    from jobreach.config.settings import SettingsStore

    store = SettingsStore(path=tmp_path / "settings.json")
    path = run_demo_generation(store)
    assert path.endswith(".csv")
