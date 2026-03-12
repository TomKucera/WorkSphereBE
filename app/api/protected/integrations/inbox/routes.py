import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.db.repositories.inbox_message_repository import InboxMessageRepository
from app.db.repositories.user_contact_repository import UserContactRepository
from app.db.repositories.work_application_repository import WorkApplicationRepository
from app.db.repositories.work_repository import WorkRepository
from app.schemas.integrations.gmail import GmailStatusResponse
from app.schemas.integrations.inbox import (
    InboxMessageAssignRequest,
    InboxMessageResponse,
    InboxMessageSuggestionResponse,
    InboxStatusResponse,
    InboxSyncResponse,
)
from app.services.integrations.gmail_service import (
    build_application_relevance_candidates,
    get_gmail_status,
    is_message_relevant,
    list_recent_message_metadata,
    read_contact_config_json,
    score_message_against_candidates,
)


router = APIRouter(prefix="/integrations/inbox", tags=["Integrations - Inbox"])


@router.get("/status", response_model=InboxStatusResponse)
def get_inbox_status(
    contact_id: int = Query(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contact_repo = UserContactRepository(db)
    inbox_repo = InboxMessageRepository(db)

    contact = contact_repo.get(contact_id, user_id)
    if not contact or contact.Type != "Email":
        raise HTTPException(status_code=404, detail="Email contact not found")

    gmail_status = get_gmail_status(read_contact_config_json(contact.ConfigJson))

    return InboxStatusResponse(
        Connected=gmail_status["connected"],
        GoogleEmail=gmail_status["google_email"],
        LastImportedReceivedAt=inbox_repo.get_last_received_at(user_id, contact_id),
        LastImportRunId=inbox_repo.get_last_import_run_id(user_id, contact_id),
        StoredMessagesCount=inbox_repo.count_active_by_contact(user_id, contact_id),
    )


@router.post("/sync", response_model=InboxSyncResponse)
def sync_inbox_messages(
    contact_id: int = Query(...),
    limit: int = Query(100, ge=1, le=200),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contact_repo = UserContactRepository(db)
    inbox_repo = InboxMessageRepository(db)
    application_repo = WorkApplicationRepository(db)
    work_repo = WorkRepository(db)

    contact = contact_repo.get(contact_id, user_id)
    if not contact or contact.Type != "Email":
        raise HTTPException(status_code=404, detail="Email contact not found")

    config = read_contact_config_json(contact.ConfigJson)
    gmail_status = get_gmail_status(config)
    if not gmail_status["connected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail is not connected for this contact",
        )

    last_received_at = inbox_repo.get_last_received_at(user_id, contact_id)
    recent_messages = list_recent_message_metadata(config=config, limit=limit, after_dt=last_received_at)

    applications = application_repo.list_by_user(user_id)
    works_by_id = {}
    for application in applications:
        if application.WorkId not in works_by_id:
            works_by_id[application.WorkId] = work_repo.get(application.WorkId)

    relevance_candidates = build_application_relevance_candidates(applications, works_by_id)
    import_run_id = str(uuid.uuid4())

    items_to_create: list[dict] = []
    for message in recent_messages:
        if inbox_repo.exists_by_gmail_message_id(user_id, contact_id, message["id"]):
            continue

        if not is_message_relevant(message, relevance_candidates):
            continue

        items_to_create.append(
            {
                "UserId": user_id,
                "UserContactId": contact_id,
                "WorkApplicationId": None,
                "GmailMessageId": message["id"],
                "GmailThreadId": message.get("thread_id"),
                "FromEmail": message.get("from"),
                "ToEmail": message.get("to"),
                "Subject": message.get("subject"),
                "Snippet": message.get("snippet"),
                "ReceivedAt": message["received_at"],
                "ImportRunId": import_run_id,
                "Active": True,
            }
        )

    created = inbox_repo.create_many(items_to_create) if items_to_create else []
    last_imported_received_at = max((item.ReceivedAt for item in created), default=None)

    return InboxSyncResponse(
        ImportRunId=import_run_id,
        ImportedCount=len(created),
        LastImportedReceivedAt=last_imported_received_at,
    )


@router.get("/messages", response_model=list[InboxMessageResponse])
def list_inbox_messages(
    contact_id: int = Query(...),
    import_run_id: str | None = Query(None),
    only_unassigned: bool = Query(False),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contact_repo = UserContactRepository(db)
    inbox_repo = InboxMessageRepository(db)

    contact = contact_repo.get(contact_id, user_id)
    if not contact or contact.Type != "Email":
        raise HTTPException(status_code=404, detail="Email contact not found")

    messages = inbox_repo.list_by_contact(
        user_id=user_id,
        contact_id=contact_id,
        import_run_id=import_run_id,
        only_unassigned=only_unassigned,
        active_only=True,
    )
    return [
        InboxMessageResponse(
            Id=message.Id,
            UserContactId=message.UserContactId,
            WorkApplicationId=message.WorkApplicationId,
            GmailMessageId=message.GmailMessageId,
            GmailThreadId=message.GmailThreadId,
            FromEmail=message.FromEmail,
            ToEmail=message.ToEmail,
            Subject=message.Subject,
            Snippet=message.Snippet,
            ReceivedAt=message.ReceivedAt,
            ImportedAt=message.ImportedAt,
            ImportRunId=message.ImportRunId,
        )
        for message in messages
    ]


@router.get("/messages/{message_id}/suggestions", response_model=list[InboxMessageSuggestionResponse])
def get_inbox_message_suggestions(
    message_id: int,
    limit: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inbox_repo = InboxMessageRepository(db)
    application_repo = WorkApplicationRepository(db)
    work_repo = WorkRepository(db)

    message = inbox_repo.get(message_id, user_id)
    if not message or not message.Active:
        raise HTTPException(status_code=404, detail="Inbox message not found")

    applications = application_repo.list_by_user(user_id)
    works_by_id = {}
    for application in applications:
        if application.WorkId not in works_by_id:
            works_by_id[application.WorkId] = work_repo.get(application.WorkId)

    candidates = build_application_relevance_candidates(applications, works_by_id)
    suggestions = score_message_against_candidates(
        {
            "from": message.FromEmail,
            "subject": message.Subject,
            "snippet": message.Snippet,
            "received_at": message.ReceivedAt,
        },
        candidates,
    )

    return [
        InboxMessageSuggestionResponse(
            WorkApplicationId=item["work_application_id"],
            WorkId=item["work_id"],
            WorkName=item["work_name"],
            Company=item["company"],
            Provider=item["provider"],
            Score=item["score"],
            Reasons=item["reasons"],
        )
        for item in suggestions[:limit]
    ]


@router.put("/messages/{message_id}/assign", response_model=InboxMessageResponse)
def assign_inbox_message(
    message_id: int,
    data: InboxMessageAssignRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inbox_repo = InboxMessageRepository(db)
    application_repo = WorkApplicationRepository(db)

    message = inbox_repo.get(message_id, user_id)
    if not message or not message.Active:
        raise HTTPException(status_code=404, detail="Inbox message not found")

    application = application_repo.get(data.WorkApplicationId)
    if not application or application.UserId != user_id:
        raise HTTPException(status_code=404, detail="Work application not found")

    inbox_repo.assign(message, data.WorkApplicationId)

    if data.Status is not None:
        application_repo.update(application, Status=data.Status)

    refreshed = inbox_repo.get(message_id, user_id)
    return InboxMessageResponse(
        Id=refreshed.Id,
        UserContactId=refreshed.UserContactId,
        WorkApplicationId=refreshed.WorkApplicationId,
        GmailMessageId=refreshed.GmailMessageId,
        GmailThreadId=refreshed.GmailThreadId,
        FromEmail=refreshed.FromEmail,
        ToEmail=refreshed.ToEmail,
        Subject=refreshed.Subject,
        Snippet=refreshed.Snippet,
        ReceivedAt=refreshed.ReceivedAt,
        ImportedAt=refreshed.ImportedAt,
        ImportRunId=refreshed.ImportRunId,
    )


@router.delete("/messages/{message_id}", status_code=204)
def delete_inbox_message(
    message_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inbox_repo = InboxMessageRepository(db)
    message = inbox_repo.get(message_id, user_id)

    if not message or not message.Active:
        raise HTTPException(status_code=404, detail="Inbox message not found")

    inbox_repo.soft_delete(message)
