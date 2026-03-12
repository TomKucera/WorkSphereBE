# Gmail Multi-Account POC (2 Emails)

This is a local concept to verify that one Google OAuth app can connect multiple Gmail accounts.

It stores per-account token config in a local JSON file:
- `accounts_tokens.json` (created automatically)

## What this proves

- One shared OAuth app (`client_id`, `client_secret`, `redirect_uri`) can authorize two different Gmail users.
- Per-user data needed for connection is mainly `refresh_token` (+ optional metadata like email/scopes).

## Prerequisites

Install required libraries (not part of current `requirements.txt`):

```bash
pip install google-api-python-client google-auth google-auth-oauthlib
```

Prepare Google OAuth client JSON (Desktop app) and set path:

```bash
export GOOGLE_OAUTH_CLIENT_SECRETS_PATH="/absolute/path/to/client_secret.json"
```

## Connect first Gmail account

```bash
python tools/concepts/gmail_multi_account_poc/gmail_multi_account_poc.py connect --account-key email_1
```

After consent, account config is saved under key `email_1`.

## Connect second Gmail account

```bash
python tools/concepts/gmail_multi_account_poc/gmail_multi_account_poc.py connect --account-key email_2
```

After consent, account config is saved under key `email_2`.

## Read messages for each account

```bash
python tools/concepts/gmail_multi_account_poc/gmail_multi_account_poc.py list --account-key email_1 --max-results 5
python tools/concepts/gmail_multi_account_poc/gmail_multi_account_poc.py list --account-key email_2 --max-results 5
```

Optional Gmail query:

```bash
python tools/concepts/gmail_multi_account_poc/gmail_multi_account_poc.py list --account-key email_1 --query "newer_than:30d"
```

## Important

- This is POC only. `refresh_token` is stored in plain JSON for simplicity.
- Production should store encrypted token in DB (`ConfigJson`) and never in local file.
