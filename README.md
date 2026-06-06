# JobReach CLI

`jobreach` is a local-first CLI for generating, reviewing, and sending cold job outreach emails from a CV and a CSV of public company or HR emails.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Configure at least one AI provider in `.env`. Gemini is the default:

```env
GEMINI_API_KEY=
JOBREACH_AI_PROVIDER=gemini
JOBREACH_AI_MODEL=gemini-1.5-flash
```

## Gmail OAuth

Create a Google OAuth desktop client with the Gmail send scope, then place the client secret at:

```text
.jobreach/credentials/google_client_secret.json
```

Authenticate locally:

```bash
jobreach auth gmail
```

The app uses Gmail OAuth and the Gmail API. It does not use SMTP and never asks for a Gmail password.

## Commands

For the guided form-style flow, run:

```bash
jobreach start
```

It asks for Gmail connection, AI provider/model, CV or profile path, leads CSV, output path, review options, send limit, delay, and final send confirmation.

Manual commands are still available:

```bash
jobreach models
jobreach auth status
jobreach profile --cv resume.pdf --out profile.json
jobreach generate --profile profile.json --leads leads.csv --out drafts.csv
jobreach review --drafts drafts.csv
jobreach send --drafts drafts.csv --confirm --limit 10 --delay-seconds 15
```

`generate` never sends email. `send` refuses unless `--confirm` is passed. `start` also asks for explicit confirmation before sending.

## Leads CSV

Required column:

```csv
email
hr@example.com
```

Optional columns include `company`, `recipient_name`, `website`, `role`, `job_url`, and `notes`.

## Local Data

Local private data lives under `.jobreach/`:

```text
.jobreach/
  credentials/
  tokens/
  logs/
  cache/
  do_not_contact.csv
```

`.jobreach/` and `.env` are gitignored.

## Safety

LLM output is validated with Pydantic. Gmail sending is deterministic code only. High-risk drafts, duplicate sends, do-not-contact emails, and drafts with missing subject/body are skipped.
