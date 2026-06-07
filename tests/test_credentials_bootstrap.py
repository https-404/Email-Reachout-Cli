from pathlib import Path

import pytest

from jobreach.mail import credentials_bootstrap


def test_bundled_client_secret_path_exists():
    path = credentials_bootstrap.bundled_client_secret_path()
    assert path is not None
    assert path.exists()


def test_ensure_oauth_copies_to_data_dir(tmp_path, monkeypatch):
    secret = tmp_path / "secret.json"
    bundled_dir = tmp_path / "bundled"
    bundled_dir.mkdir()
    bundled_file = bundled_dir / "google_client_secret.json"
    bundled_file.write_text('{"installed":{"client_id":"real-id","client_secret":"real-secret"}}', encoding="utf-8")

    monkeypatch.setattr(credentials_bootstrap, "google_client_secret_path", lambda: secret)
    monkeypatch.setattr(credentials_bootstrap, "credentials_dir", lambda: tmp_path)
    monkeypatch.setattr(credentials_bootstrap, "bundled_client_secret_path", lambda: bundled_file)

    target = credentials_bootstrap.ensure_oauth_client_secret()
    assert target.exists()
    assert "real-id" in target.read_text(encoding="utf-8")
