# Campaigns, CRM, and follow-ups

JobReach stores campaign history in SQLite at `~/.jobreach/crm/jobreach.db`. Draft batches remain in CSV for portability.

## Shell commands

| Command | Description |
|---------|-------------|
| `campaigns` | List campaigns |
| `new campaign` | Create a named campaign (optional CV/leads paths) |
| `mark replied <email>` | Mark contact as replied; optional DNC prompt |
| `dnc list` / `dnc add` / `dnc remove` | Manage do-not-contact list |
| `follow up` | Create follow-up draft batch for no-reply contacts after N days (default 7, see settings) |
| `export campaign` | Markdown report in `~/.jobreach/exports/` |

## Send queue

When sending, choose **Queue across days** to spread approved drafts with `scheduled_at` timestamps.

- `send queue status` — view queued items
- `send queue run` — send due items within daily cap and send window

## Settings

- `daily_send_cap` (default 50)
- `send_window_start` / `send_window_end` (local time, default 09:00–17:00)
- `follow_up_days` (default 7)

## Data model

- **campaigns** — name, paths, tone, provider, model
- **contacts** — email, company, reply_status, last_contacted_at
- **send_events** — per-send audit trail
- **send_queue** — scheduled sends

Draft CSVs include `follow_up_of`, `reply_status`, and `quality_reason` for review context.
