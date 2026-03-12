from app.schemas.base.base_model import ApiBaseModel


class GmailConnectUrlResponse(ApiBaseModel):
    AuthUrl: str


class GmailCallbackResponse(ApiBaseModel):
    Success: bool
    Message: str


class GmailStatusResponse(ApiBaseModel):
    Connected: bool
    GoogleEmail: str | None = None
    Scopes: list[str] = []


class GmailMessageItem(ApiBaseModel):
    Id: str
    ThreadId: str | None = None
    Snippet: str | None = None
    InternalDate: str | None = None
    From: str | None = None
    To: str | None = None
    Subject: str | None = None
    Date: str | None = None
