from datetime import datetime

from app.schemas.base.base_model import ApiBaseModel

class CvFilter(ApiBaseModel):
    Name: str | None = None
    Note: str | None = None
    OriginalFileName: str | None = None
    Active: bool | None = None
    CreatedFrom: datetime | None = None
    CreatedTo: datetime | None = None
    UpdatedFrom: datetime | None = None
    UpdatedTo: datetime | None = None
