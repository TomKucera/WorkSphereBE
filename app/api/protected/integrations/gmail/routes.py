from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.db.repositories.user_contact_repository import UserContactRepository
from app.schemas.integrations.gmail import (
    GmailConnectUrlResponse,
    GmailMessageItem,
    GmailStatusResponse,
)
from app.services.integrations.gmail_service import (
    build_auth_url,
    get_gmail_status,
    list_latest_messages,
    read_contact_config_json,
)


router = APIRouter(prefix="/integrations/gmail", tags=["Integrations - Gmail"])


@router.get("/connect-url", response_model=GmailConnectUrlResponse)
def get_connect_url(
    contact_id: int = Query(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = UserContactRepository(db)
    contact = repo.get(contact_id, user_id)

    if not contact or contact.Type != "Email":
        raise HTTPException(status_code=404, detail="Email contact not found")

    auth_url = build_auth_url(user_id=user_id, contact_id=contact_id)
    return GmailConnectUrlResponse(AuthUrl=auth_url)


@router.get("/status", response_model=GmailStatusResponse)
def get_gmail_status_for_contact(
    contact_id: int = Query(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = UserContactRepository(db)
    contact = repo.get(contact_id, user_id)

    if not contact or contact.Type != "Email":
        raise HTTPException(status_code=404, detail="Email contact not found")

    status_data = get_gmail_status(read_contact_config_json(contact.ConfigJson))
    return GmailStatusResponse(
        Connected=status_data["connected"],
        GoogleEmail=status_data["google_email"],
        Scopes=status_data["scopes"],
    )


@router.get("/messages", response_model=list[GmailMessageItem])
def get_latest_messages(
    contact_id: int = Query(...),
    limit: int = Query(10, ge=1, le=50),
    query: str | None = Query(None),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = UserContactRepository(db)
    contact = repo.get(contact_id, user_id)

    if not contact or contact.Type != "Email":
        raise HTTPException(status_code=404, detail="Email contact not found")

    config = read_contact_config_json(contact.ConfigJson)
    if "gmail" not in config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail is not connected for this contact",
        )

    items = list_latest_messages(config=config, limit=limit, query=query)
    return [
        GmailMessageItem(
            Id=item["id"],
            ThreadId=item.get("thread_id"),
            Snippet=item.get("snippet"),
            InternalDate=item.get("internal_date"),
            From=item.get("from"),
            To=item.get("to"),
            Subject=item.get("subject"),
            Date=item.get("date"),
        )
        for item in items
    ]
