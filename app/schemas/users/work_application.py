from typing import Literal
from pydantic import constr
from datetime import datetime

from app.schemas.base.base_model import ApiBaseModel

ApplicationStatus = Literal[
    "SUBMITTED",
    "VIEWED",
    "REJECTED",
    "ACCEPTED",
]

class WorkApplicationCreate(ApiBaseModel):
    WorkId: int
    CvId: int
    ContactEmailId: int
    ContactPhoneId: int
    Message: constr(max_length=1000) | None = None   # type: ignore

class WorkApplicationUpdate(ApiBaseModel):
    Status: ApplicationStatus | None = None


class WorkApplicationResponse(ApiBaseModel):
    Id: int

    UserId: int
    WorkId: int
    CvId: int

    FirstName: str
    LastName: str

    Email: str
    Phone: str

    Message: str | None

    Status: ApplicationStatus

    CreatedAt: datetime
    UpdatedAt: datetime | None

    class Config:
        from_attributes = True