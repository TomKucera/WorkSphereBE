import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import ALGORITHM, SECRET_KEY, decrypt_text, encrypt_text


def _require_google_oauth_config() -> tuple[str, str, str]:
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = settings.GOOGLE_REDIRECT_URI

    if not client_id or not client_secret or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured",
        )

    return client_id, client_secret, redirect_uri


def _google_scopes() -> list[str]:
    scopes = [s.strip() for s in settings.GOOGLE_GMAIL_SCOPES.split(",")]
    return [s for s in scopes if s]


JOB_RELATED_KEYWORDS = [
    "application",
    "applied",
    "applying",
    "candidate",
    "career",
    "hiring",
    "interview",
    "job",
    "position",
    "recruit",
    "recruiter",
    "response to your application",
    "thank you for applying",
    "vacancy",
    "vyberove",
    "pozice",
    "pohovor",
    "prihlask",
]


def _google_client_config() -> dict[str, Any]:
    client_id, client_secret, redirect_uri = _require_google_oauth_config()

    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }


def _load_google_libs():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import Flow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google API libraries are not installed",
        ) from exc

    return Request, Credentials, Flow, build


def create_oauth_state(user_id: int, contact_id: int, code_verifier: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    payload = {
        "typ": "gmail_oauth_state",
        "sub": str(user_id),
        "contact_id": contact_id,
        "code_verifier": code_verifier,
        "exp": exp,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def parse_oauth_state(state_token: str) -> tuple[int, int, str]:
    try:
        payload = jwt.decode(state_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("typ") != "gmail_oauth_state":
            raise ValueError("Invalid state type")

        user_id = int(payload["sub"])
        contact_id = int(payload["contact_id"])
        code_verifier = str(payload["code_verifier"])
        return user_id, contact_id, code_verifier

    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state",
        )


def build_auth_url(user_id: int, contact_id: int) -> str:
    _, _, redirect_uri = _require_google_oauth_config()
    _, _, Flow, _ = _load_google_libs()
    code_verifier = secrets.token_urlsafe(64)

    flow = Flow.from_client_config(
        _google_client_config(),
        scopes=_google_scopes(),
        code_verifier=code_verifier,
    )
    flow.redirect_uri = redirect_uri

    state_token = create_oauth_state(user_id, contact_id, code_verifier)

    auth_url, _ = flow.authorization_url(
        state=state_token,
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        code_challenge_method="S256",
    )
    return auth_url


def exchange_code_for_gmail_config(code: str, code_verifier: str) -> dict[str, Any]:
    _, _, redirect_uri = _require_google_oauth_config()
    Request, Credentials, Flow, build = _load_google_libs()

    flow = Flow.from_client_config(
        _google_client_config(),
        scopes=_google_scopes(),
        code_verifier=code_verifier,
    )
    flow.redirect_uri = redirect_uri
    flow.fetch_token(code=code)

    creds = flow.credentials

    if not creds.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return refresh token. Reconnect with consent.",
        )

    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()

    return {
        "gmail": {
            "google_email": profile.get("emailAddress"),
            "refresh_token_enc": encrypt_text(creds.refresh_token),
            "scopes": list(creds.scopes or _google_scopes()),
        }
    }


def read_contact_config_json(config_json: str | None) -> dict[str, Any]:
    if not config_json:
        return {}
    try:
        parsed = json.loads(config_json)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def get_gmail_status(config: dict[str, Any]) -> dict[str, Any]:
    gmail_cfg = config.get("gmail") or {}
    return {
        "connected": bool(gmail_cfg.get("refresh_token_enc") or gmail_cfg.get("refresh_token")),
        "google_email": gmail_cfg.get("google_email"),
        "scopes": gmail_cfg.get("scopes") or [],
    }


def _normalize_text(value: str | None) -> str:
    return (value or "").casefold()


def _extract_significant_tokens(value: str | None) -> list[str]:
    raw = _normalize_text(value)
    tokens = [token.strip(".,:;!?()[]{}<>-_/\\\"'") for token in raw.split()]
    return [token for token in tokens if len(token) >= 5]


def _contains_any(haystack: str, needles: list[str]) -> bool:
    return any(needle in haystack for needle in needles if needle)


def is_message_relevant(message: dict[str, Any], application_candidates: list[dict[str, Any]]) -> bool:
    haystack = " ".join(
        [
            _normalize_text(message.get("from")),
            _normalize_text(message.get("subject")),
            _normalize_text(message.get("snippet")),
        ]
    )

    keyword_hit = _contains_any(haystack, JOB_RELATED_KEYWORDS)

    best_score = 0

    for candidate in application_candidates:
        score = 0
        if candidate["company"] and candidate["company"] in haystack:
            score += 3

        if candidate["provider"] and candidate["provider"] in haystack:
            score += 2

        matched_name_tokens = [token for token in candidate["name_tokens"] if token in haystack]
        score += min(len(matched_name_tokens), 2)

        if message["received_at"] >= candidate["created_at"]:
            score += 1

        if score > best_score:
            best_score = score

    if best_score >= 3:
        return True

    return keyword_hit and best_score >= 2


def build_gmail_credentials_from_contact_config(config: dict[str, Any]):
    client_id, client_secret, _ = _require_google_oauth_config()
    Request, Credentials, _, _ = _load_google_libs()

    gmail_cfg = config.get("gmail") or {}
    refresh_token_enc = gmail_cfg.get("refresh_token_enc")
    legacy_refresh_token = gmail_cfg.get("refresh_token")
    refresh_token = decrypt_text(refresh_token_enc) if refresh_token_enc else legacy_refresh_token
    scopes = gmail_cfg.get("scopes") or _google_scopes()

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail is not connected for this contact",
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )
    creds.refresh(Request())
    return creds


def list_latest_messages(config: dict[str, Any], limit: int = 10, query: str | None = None) -> list[dict[str, Any]]:
    _, _, _, build = _load_google_libs()
    creds = build_gmail_credentials_from_contact_config(config)
    service = build("gmail", "v1", credentials=creds)

    list_response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=limit,
            q=query or "",
            labelIds=["INBOX"],
        )
        .execute()
    )

    items = list_response.get("messages", [])
    results: list[dict[str, Any]] = []

    for item in items:
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=item["id"],
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            )
            .execute()
        )

        headers = {
            h.get("name", ""): h.get("value", "")
            for h in msg.get("payload", {}).get("headers", [])
        }

        results.append(
            {
                "id": msg.get("id"),
                "thread_id": msg.get("threadId"),
                "snippet": msg.get("snippet"),
                "internal_date": msg.get("internalDate"),
                "from": headers.get("From"),
                "to": headers.get("To"),
                "subject": headers.get("Subject"),
                "date": headers.get("Date"),
            }
        )

    return results


def list_recent_message_metadata(
    config: dict[str, Any],
    limit: int = 100,
    after_dt: datetime | None = None,
) -> list[dict[str, Any]]:
    _, _, _, build = _load_google_libs()
    creds = build_gmail_credentials_from_contact_config(config)
    service = build("gmail", "v1", credentials=creds)

    query_parts: list[str] = []
    if after_dt is not None:
        timestamp = int(after_dt.replace(tzinfo=timezone.utc).timestamp())
        query_parts.append(f"after:{timestamp}")

    gmail_query = " ".join(query_parts)

    list_response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=limit,
            q=gmail_query,
            labelIds=["INBOX"],
        )
        .execute()
    )

    items = list_response.get("messages", [])
    results: list[dict[str, Any]] = []

    for item in items:
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=item["id"],
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            )
            .execute()
        )

        headers = {
            h.get("name", ""): h.get("value", "")
            for h in msg.get("payload", {}).get("headers", [])
        }

        internal_date_raw = msg.get("internalDate")
        internal_date = (
            datetime.fromtimestamp(int(internal_date_raw) / 1000, tz=timezone.utc).replace(tzinfo=None)
            if internal_date_raw
            else datetime.now(timezone.utc).replace(tzinfo=None)
        )

        results.append(
            {
                "id": msg.get("id"),
                "thread_id": msg.get("threadId"),
                "snippet": msg.get("snippet"),
                "internal_date": internal_date_raw,
                "received_at": internal_date,
                "from": headers.get("From"),
                "to": headers.get("To"),
                "subject": headers.get("Subject"),
                "date": headers.get("Date"),
            }
        )

    return results


def build_application_relevance_candidates(applications: list[Any], works_by_id: dict[int, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    for application in applications:
        work = works_by_id.get(application.WorkId)
        if not work:
            continue

        candidates.append(
            {
                "application_id": application.Id,
                "work_id": application.WorkId,
                "work_name": work.Name,
                "company": _normalize_text(work.Company),
                "company_name": work.Company,
                "provider": _normalize_text(work.Provider),
                "provider_name": work.Provider,
                "name_tokens": _extract_significant_tokens(work.Name),
                "created_at": application.CreatedAt,
            }
        )

    return candidates


def score_message_against_candidates(
    message: dict[str, Any],
    application_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    haystack = " ".join(
        [
            _normalize_text(message.get("from")),
            _normalize_text(message.get("subject")),
            _normalize_text(message.get("snippet")),
        ]
    )

    suggestions: list[dict[str, Any]] = []

    for candidate in application_candidates:
        score = 0
        reasons: list[str] = []

        if candidate["company"] and candidate["company"] in haystack:
            score += 3
            reasons.append("company")

        if candidate["provider"] and candidate["provider"] in haystack:
            score += 2
            reasons.append("provider")

        matched_name_tokens = [token for token in candidate["name_tokens"] if token in haystack]
        if matched_name_tokens:
            score += min(len(matched_name_tokens), 2)
            reasons.append("work_name")

        if message["received_at"] >= candidate["created_at"]:
            score += 1
            reasons.append("time_proximity")

        if score <= 0:
            continue

        suggestions.append(
            {
                "work_application_id": candidate["application_id"],
                "work_id": candidate["work_id"],
                "work_name": candidate["work_name"],
                "company": candidate["company_name"],
                "provider": candidate["provider_name"],
                "score": score,
                "reasons": reasons,
            }
        )

    suggestions.sort(key=lambda item: (-item["score"], item["work_application_id"]))
    return suggestions
