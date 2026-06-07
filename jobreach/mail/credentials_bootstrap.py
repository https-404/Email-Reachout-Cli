import shutil
from importlib import resources
from pathlib import Path

from jobreach.config.paths import credentials_dir, google_client_secret_path
from jobreach.core.errors import GmailAuthError

PLACEHOLDER_MARKERS = ("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET")


def bundled_client_secret_path() -> Path | None:
    try:
        with resources.as_file(resources.files("jobreach.credentials") / "google_client_secret.json") as path:
            if path.exists():
                return Path(path)
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        pass
    fallback = Path(__file__).resolve().parent / "credentials" / "google_client_secret.json"
    return fallback if fallback.exists() else None


def _is_placeholder(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return any(marker in text for marker in PLACEHOLDER_MARKERS)


def ensure_oauth_client_secret() -> Path:
    target = google_client_secret_path()
    credentials_dir().mkdir(parents=True, exist_ok=True)
    if target.exists() and not _is_placeholder(target):
        return target

    bundled = bundled_client_secret_path()
    if bundled and bundled.exists() and not _is_placeholder(bundled):
        shutil.copy2(bundled, target)
        return target

    if target.exists():
        return target

    if bundled and bundled.exists():
        shutil.copy2(bundled, target)

    if not target.exists():
        raise GmailAuthError(
            "Gmail OAuth is not configured for this install.\n"
            "The maintainer must replace jobreach/credentials/google_client_secret.json "
            "with a real Google Desktop OAuth client before release."
        )
    if _is_placeholder(target):
        raise GmailAuthError(
            "Gmail OAuth client secret is still a placeholder.\n"
            "Replace ~/.jobreach/credentials/google_client_secret.json with your "
            "Google Cloud Desktop OAuth JSON, or reinstall a release build with bundled credentials."
        )
    return target
