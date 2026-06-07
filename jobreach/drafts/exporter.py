from pathlib import Path

from jobreach.drafts.index import list_batches
from jobreach.drafts.store import load_drafts
from jobreach.logs.sent_log import SentLog


def export_campaign_report(name: str, output_dir: Path) -> Path:
    batches = list_batches()
    sent = SentLog()._rows()
    lines = [
        f"# JobReach Campaign Report: {name}",
        "",
        f"Draft batches: {len(batches)}",
        f"Total sent: {len(sent)}",
        "",
        "## Batches",
    ]
    for batch in batches:
        drafts = load_drafts(batch.path)
        lines.append(
            f"- {batch.id}: {len(drafts)} drafts, {batch.approved} approved, {batch.sent} sent"
        )
    lines.extend(["", "## Recent sends", ""])
    for row in sent[-20:]:
        lines.append(f"- {row.get('sent_at', '')} {row.get('email', '')} — {row.get('subject', '')}")

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"report_{name.replace(' ', '_')}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
