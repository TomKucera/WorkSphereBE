from app.schemas.base.base_model import ApiBaseModel
from datetime import datetime

class CvListItem(ApiBaseModel):
    Id: int
    UserId: int
    Name: str
    Note: str | None
    OriginalFileName: str

    # ContentType: str | None = None
    # ExtractedText: str | None = None

    Active: bool

    CreatedAt: datetime
    UpdatedAt: datetime | None
    
    class Config:
        from_attributes = True
