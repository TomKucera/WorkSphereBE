import argparse
import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
BASE_DIR = Path(__file__).resolve().parent
STORE_PATH = BASE_DIR / "accounts_tokens.json"


def load_store() -> dict:
    if not STORE_PATH.exists():
        return {"accounts": {}}
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    STORE_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")


def get_client_secrets_path(cli_value: str | None) -> str:
    path = cli_value or os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS_PATH")
    if not path:
        raise RuntimeError(
            "Missing client secrets path. Use --client-secrets or GOOGLE_OAUTH_CLIENT_SECRETS_PATH."
        )
    if not Path(path).exists():
        raise RuntimeError(f"Client secrets file not found: {path}")
    return path


def connect_account(account_key: str, client_secrets_path: str) -> None:
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )

    if not creds.refresh_token:
        raise RuntimeError(
            "No refresh token returned. Revoke previous app consent and try again with prompt=consent."
        )

    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    google_email = profile.get("emailAddress")

    store = load_store()
    store["accounts"][account_key] = {
        "google_email": google_email,
        "refresh_token": creds.refresh_token,
        "scopes": list(creds.scopes or SCOPES),
    }
    save_store(store)

    print(f"Connected account key: {account_key}")
    print(f"Gmail address: {google_email}")
    print(f"Saved to: {STORE_PATH}")


def build_credentials_from_store(account: dict, client_secrets_path: str) -> Credentials:
    with open(client_secrets_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    cfg = raw.get("installed") or raw.get("web")
    if not cfg:
        raise RuntimeError("Invalid client secrets JSON (missing 'installed' or 'web').")

    creds = Credentials(
        token=None,
        refresh_token=account["refresh_token"],
        token_uri=cfg["token_uri"],
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        scopes=account.get("scopes") or SCOPES,
    )
    creds.refresh(Request())
    return creds


def list_messages(account_key: str, client_secrets_path: str, max_results: int, query: str | None) -> None:
    store = load_store()
    account = store.get("accounts", {}).get(account_key)
    if not account:
        raise RuntimeError(f"Account key not found: {account_key}")

    creds = build_credentials_from_store(account, client_secrets_path)
    service = build("gmail", "v1", credentials=creds)

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results,
            q=query or "",
            labelIds=["INBOX"],
        )
        .execute()
    )

    messages = response.get("messages", [])
    print(f"Account key: {account_key}")
    print(f"Gmail: {account.get('google_email')}")
    print(f"Messages fetched: {len(messages)}")

    for idx, item in enumerate(messages, start=1):
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=item["id"], format="metadata", metadataHeaders=["Subject", "From", "Date"])
            .execute()
        )
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        print(f"{idx}. id={item['id']}")
        print(f"   From: {headers.get('From', '-')}")
        print(f"   Date: {headers.get('Date', '-')}")
        print(f"   Subject: {headers.get('Subject', '-')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="POC: connect/list Gmail for multiple accounts.")
    parser.add_argument("--client-secrets", help="Path to Google OAuth client secrets JSON.")

    sub = parser.add_subparsers(dest="command", required=True)

    connect_cmd = sub.add_parser("connect", help="Authorize and save account refresh token.")
    connect_cmd.add_argument("--account-key", required=True, help="Local key, e.g. email_1 or email_2.")

    list_cmd = sub.add_parser("list", help="List inbox messages for saved account.")
    list_cmd.add_argument("--account-key", required=True, help="Saved account key.")
    list_cmd.add_argument("--max-results", type=int, default=5)
    list_cmd.add_argument("--query", help="Optional Gmail search query.")

    args = parser.parse_args()
    client_secrets_path = get_client_secrets_path(args.client_secrets)

    if args.command == "connect":
        connect_account(args.account_key, client_secrets_path)
        return

    if args.command == "list":
        list_messages(args.account_key, client_secrets_path, args.max_results, args.query)
        return

    raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
