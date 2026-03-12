import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import base64

from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "token.json"
CREDS_FILE = "/Users/tomaskucera/Downloads/client_secret_684195231984-ib1f0l18k84qr676bd2pivqadlnsd8ov.apps.googleusercontent.com.json"
# export GOOGLE_OAUTH_CLIENT_SECRETS_PATH="/Users/tomaskucera/Downloads/client_secret_684195231984-ib1f0l18k84qr676bd2pivqadlnsd8ov.apps.googleusercontent.com.json"
def get_gmail_service():
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid creds → login once
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # silent refresh
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def decode(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode()).decode(errors="ignore")


def extract_text(service, user_id, msg_id, part):
    # Inline text
    data = part.get("body", {}).get("data")
    if data:
        return decode(data)

    # Large body stored as attachment
    attachment_id = part.get("body", {}).get("attachmentId")
    if attachment_id:
        att = service.users().messages().attachments().get(
            userId=user_id,
            messageId=msg_id,
            id=attachment_id
        ).execute()
        return decode(att.get("data", ""))

    # Recursive search in nested parts
    for sub in part.get("parts", []):
        text = extract_text(service, user_id, msg_id, sub)
        if text:
            return text

    return ""


def get_messages(dt: datetime = datetime.now() - timedelta(days=10), limit=100)->list[dict]:

    service = get_gmail_service()

    timestamp = int(dt.timestamp())

    query = f"after:{timestamp}"

    # Step 1: list message IDs
    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=limit,
        labelIds=["INBOX"],
    ).execute()



    messages = results.get("messages", [])
    full_messages = []

    for m in messages:
        msg = service.users().messages().get(
            userId="me",
            id=m["id"],
            format="full"
        ).execute()

        text = extract_text(service, "me", msg["id"], msg["payload"])

        full_messages.append({
            "id": msg["id"],
            "threadId": msg["threadId"],
            "snippet": msg.get("snippet"),
            "internalDate": msg.get("internalDate"),
            "text": text,  # ← FULL BODY HERE
        })

    for m in full_messages:
        print(f"INDEX: { full_messages.index(m) }")
        print(f"Message ID: {m['id']}")
        print(f"Thread ID: {m['threadId']}")
        print(f"Snippet: {m['snippet']}")
        print(f"Internal Date: {datetime.fromtimestamp(int(m['internalDate'])/1000)}")
        print(f"Full Text:\n{m['text'][:500]}...")

    return full_messages


    

    # print (full_messages[0].keys())
    # dict_keys(['id', 'threadId', 'labelIds', 'snippet', 'payload', 'sizeEstimate', 'historyId', 'internalDate'])


   
