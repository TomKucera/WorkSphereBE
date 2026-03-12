from datetime import datetime

from app.schemas.base.base_model import ApiBaseModel
from app.schemas.users.work_application import ApplicationStatus


class InboxStatusResponse(ApiBaseModel):
    Connected: bool
    GoogleEmail: str | None = None
    LastImportedReceivedAt: datetime | None = None
    LastImportRunId: str | None = None
    StoredMessagesCount: int


class InboxSyncResponse(ApiBaseModel):
    ImportRunId: str
    ImportedCount: int
    LastImportedReceivedAt: datetime | None = None


class InboxMessageResponse(ApiBaseModel):
    Id: int
    UserContactId: int
    WorkApplicationId: int | None = None
    GmailMessageId: str
    GmailThreadId: str | None = None
    FromEmail: str | None = None
    ToEmail: str | None = None
    Subject: str | None = None
    Snippet: str | None = None
    ReceivedAt: datetime
    ImportedAt: datetime
    ImportRunId: str

    class Config:
        from_attributes = True


class InboxMessageAssignRequest(ApiBaseModel):
    WorkApplicationId: int
    Status: ApplicationStatus | None = None


class InboxMessageSuggestionResponse(ApiBaseModel):
    WorkApplicationId: int
    WorkId: int
    WorkName: str
    Company: str
    Provider: str
    Score: int
    Reasons: list[str]
