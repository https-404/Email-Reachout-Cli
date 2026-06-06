import json
from pathlib import Path

from jobreach.config.paths import run_log_path
from jobreach.utils.files import ensure_parent
from jobreach.utils.time import utc_now_iso


def record_run(event: str, payload: dict, path: str | Path | None = None) -> None:
    target = Path(path) if path else run_log_path()
    ensure_parent(target)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": utc_now_iso(), "event": event, "payload": payload}) + "\n")
