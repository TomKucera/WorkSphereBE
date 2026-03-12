import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.repositories.user_contact_repository import UserContactRepository
from app.schemas.integrations.gmail import GmailCallbackResponse
from app.services.integrations.gmail_service import (
    exchange_code_for_gmail_config,
    parse_oauth_state,
    read_contact_config_json,
)


router = APIRouter(prefix="/integrations/gmail", tags=["Integrations - Gmail"])


@router.get("/callback", response_model=GmailCallbackResponse)
def gmail_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth callback parameters")

    user_id, contact_id, code_verifier = parse_oauth_state(state)

    repo = UserContactRepository(db)
    contact = repo.get(contact_id, user_id)
    if not contact or contact.Type != "Email":
        raise HTTPException(status_code=404, detail="Email contact not found")

    gmail_cfg = exchange_code_for_gmail_config(code, code_verifier)

    config = read_contact_config_json(contact.ConfigJson)
    config.update(gmail_cfg)

    contact.ConfigJson = json.dumps(config)
    db.commit()

    return GmailCallbackResponse(
        Success=True,
        Message="Gmail connected successfully",
    )
