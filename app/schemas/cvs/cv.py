from datetime import datetime
from app.schemas.base.base_model import ApiBaseModel


class CvBase(ApiBaseModel):
    OriginalFileName: str
    ContentType: str | None = None
    Language: str | None = None


class CvRead(CvBase):
    Id: int
    UserId: int
    Active: bool
    CreatedAt: datetime
    UpdatedAt: datetime | None = None

    class Config:
        from_attributes = True
