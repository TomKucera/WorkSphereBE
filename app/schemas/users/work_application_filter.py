from datetime import datetime

from app.schemas.base.base_model import ApiBaseModel

from app.schemas.users.work_application import (
    ApplicationStatus
)

class WorkApplicationFilter(ApiBaseModel):
    WorkProvider: str | None = None
    WorkCompany: str | None = None
    WorkName: str | None = None
    # WorkAddedByScanId: int | None = None
    # WorkRemovedByScanId: int | None = None
    
    Phone: str | None = None
    Email: str | None = None
    # CvId: int
    Message: str | None = None
    Status: list[ApplicationStatus] | None = None
    CreatedFrom: datetime | None = None
    CreatedTo: datetime | None = None
    UpdatedFrom: datetime | None = None
    UpdatedTo: datetime | None = None
