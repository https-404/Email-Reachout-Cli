from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from jobreach.config.paths import drafts_index_path
from jobreach.drafts.store import load_drafts
from jobreach.utils.json_utils import read_json, write_json


@dataclass
class DraftBatch:
    id: str
    path: str
    created_at: str
    count: int
    approved: int
    sent: int
    provider: str
    model: str


def _index_path() -> Path:
    return drafts_index_path()


def list_batches() -> list[DraftBatch]:
    path = _index_path()
    if not path.exists():
        return []
    raw = read_json(path)
    return [DraftBatch(**entry) for entry in raw]


def add_batch(
    batch_id: str,
    path: str,
    count: int,
    provider: str,
    model: str,
) -> DraftBatch:
    batches = list_batches()
    batch = DraftBatch(
        id=batch_id,
        path=path,
        created_at=datetime.now(timezone.utc).isoformat(),
        count=count,
        approved=0,
        sent=0,
        provider=provider,
        model=model,
    )
    batches.insert(0, batch)
    write_json(_index_path(), [batch.__dict__ for batch in batches])
    return batch


def update_batch_stats(batch_id: str) -> None:
    batches = list_batches()
    updated: list[dict] = []
    for batch in batches:
        data = batch.__dict__
        if batch.id == batch_id:
            drafts = load_drafts(batch.path)
            data["count"] = len(drafts)
            data["approved"] = sum(1 for draft in drafts if draft.status == "approved")
            data["sent"] = sum(1 for draft in drafts if draft.status == "sent")
        updated.append(data)
    write_json(_index_path(), updated)


def get_batch(batch_id: str) -> DraftBatch | None:
    for batch in list_batches():
        if batch.id == batch_id:
            return batch
    return None
