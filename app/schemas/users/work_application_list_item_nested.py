from datetime import datetime

from app.schemas.base.base_model import ApiBaseModel

from app.schemas.users.work_application import (
    ApplicationStatus
)

class WorkApplicationListItemNested(ApiBaseModel):
    Id: int
    
    Status: ApplicationStatus
    CreatedAt: datetime
    UpdatedAt: datetime | None
    
    class Config:
        from_attributes = True
