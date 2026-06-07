# Google OAuth for JobReach

JobReach bundles a **Desktop OAuth client** in the package. Users only sign in with Google once; they do not create their own Google Cloud project.

## Maintainer checklist (before public release)

1. Create **one** Google Cloud project for JobReach.
2. Enable the **Gmail API**.
3. Configure the **OAuth consent screen** (External).
4. Add scope: `https://www.googleapis.com/auth/gmail.send`
5. Create an OAuth client of type **Desktop app**.
6. Download the JSON and replace `jobreach/credentials/google_client_secret.json` (remove placeholder markers).
7. Add test users while in **Testing** mode (up to 100).
8. Plan [Google verification](https://support.google.com/cloud/answer/9110914) before scaling beyond test users.

## User experience

- On first `auth gmail`, JobReach copies bundled credentials to `~/.jobreach/credentials/google_client_secret.json` if needed.
- Users choose browser or manual code flow; no file-path setup required.

## Production publish

- Submit OAuth consent for verification when moving out of Testing.
- Document privacy policy URL on the consent screen.
- Restrict redirect URIs to installed-app defaults (`http://localhost`).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Placeholder client error | Maintainer must ship real OAuth JSON |
| Access blocked (403) | Add user as test user or complete verification |
| Browser flow fails | Use manual link + paste authorization code |
