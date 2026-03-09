from app.schemas.base.base_model import ApiBaseModel
from datetime import datetime

from app.schemas.users.work_application import (
    ApplicationStatus, ApplicationType
)

from app.schemas.works.work_list_item_nested import (
    WorkListItemNested
)

class WorkApplicationListItem(ApiBaseModel):
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
    ApplicationType: ApplicationType

    CreatedAt: datetime
    UpdatedAt: datetime | None

    Work: WorkListItemNested   # nested object for work data

    class Config:
        from_attributes = True
