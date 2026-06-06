import json
from pathlib import Path

import pytest

from jobreach.config.settings import AppSettings, SettingsStore


def test_settings_store_defaults(tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    settings = store.load()
    assert settings.default_provider is None
    assert settings.temperature == 0.4
    assert settings.first_run_complete is False


def test_settings_store_save_and_update(tmp_path: Path):
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    store.save(AppSettings(default_provider="openai", default_model="gpt-4o-mini", first_run_complete=True))
    loaded = store.load()
    assert loaded.default_provider == "openai"
    assert loaded.default_model == "gpt-4o-mini"
    assert loaded.first_run_complete is True

    updated = store.update(send_delay_seconds=30)
    assert updated.send_delay_seconds == 30
    assert json.loads(path.read_text())["send_delay_seconds"] == 30
