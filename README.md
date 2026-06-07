# JobReach CLI

JobReach is a local-first interactive CLI for generating, reviewing, and sending cold job outreach emails from your CV and a CSV of public company or HR emails.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
jobreach
```

Running `jobreach` with no arguments opens the interactive shell:

```text
JobReach>

Type "help" for commands.
```

On first launch, JobReach walks you through:

1. Choosing an AI provider (OpenAI, Gemini, or Anthropic)
2. Entering your API key (stored in your OS keychain — not in plain text)
3. Selecting a default model
4. Optionally connecting Gmail

No `.env` file is required for normal use.

## Shell commands

```text
help                Show available commands
status              Show configuration, batches, and stats
settings            Open settings menu
preview leads       Validate and preview a leads CSV
generate drafts     Generate drafts (remembers last CV/leads paths)
review drafts       Edit, regenerate, approve; resume where you left off
send emails         Send, dry-run, or queue across days
campaigns           List campaigns (SQLite CRM)
follow up           Create follow-up batch for no-reply contacts
demo                Try with sample data — no API keys
auth gmail          Connect Gmail (bundled OAuth)
exit / quit         Close JobReach
```

Full list: type `help` in the shell. See [docs/CAMPAIGNS.md](docs/CAMPAIGNS.md) for CRM, DNC, and scheduling.

Sending requires typing exactly `SEND` to confirm (or `SEND HIGH RISK` for high-risk drafts). Only approved drafts are sent.

## Gmail OAuth

JobReach **bundles OAuth client credentials** in the package. You only sign in with Google — no Google Cloud Console setup required.

```text
JobReach> auth gmail
```

Credentials are copied automatically to `~/.jobreach/credentials/` on first use. See [docs/GOOGLE_OAUTH.md](docs/GOOGLE_OAUTH.md) for maintainer verification steps.

You can choose:

1. **Open browser** — automatic sign-in (default)
2. **Copy link + paste code** — use this if the browser does not open (remote SSH, restricted terminals, etc.)

From settings you can also type option names instead of numbers:

```text
JobReach> settings
Choose an option: gmail
Choose an option: manual
```

JobReach uses Gmail OAuth and the Gmail API. It does not use SMTP and never asks for your Gmail password.

## Local data

```text
~/.jobreach/
  config/settings.json
  config/provider_models_cache.json
  tokens/gmail_token.json
  credentials/google_client_secret.json
  drafts/
  logs/sent_log.csv
  profiles/
  do_not_contact.csv
```

If you previously used `./.jobreach` in a project folder, JobReach migrates it to `~/.jobreach` on first shell launch.

## Leads CSV

Required column:

```csv
email
hr@example.com
```

Optional columns: `company`, `recipient_name`, `website`, `role`, `job_url`, `notes`

## Advanced / legacy CLI

Flag-based commands remain available for power users and scripting:

```bash
jobreach generate --cv resume.pdf --leads leads.csv --out drafts.csv
jobreach review --drafts drafts.csv
jobreach send --drafts drafts.csv --confirm --approved-only
jobreach auth gmail
jobreach start
```

Legacy commands read API keys from environment variables. Copy `.env.example` to `.env` if you use them:

```bash
cp .env.example .env
```

## Safety

- LLM output is validated with Pydantic
- Gmail sending is deterministic code only
- High-risk drafts, duplicate sends, do-not-contact emails, and unapproved drafts are skipped in the interactive send flow
- API keys are stored in the OS keychain, never in settings JSON

## Development

```bash
pip install -e ".[dev]"
pytest
python -m jobreach
```

## Releasing

See [RELEASE.md](RELEASE.md) for version bumps, tagging, GitHub Releases, and optional PyPI publish.

```bash
make build          # test + build
make release-check  # validate dist/
```
