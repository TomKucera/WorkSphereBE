from datetime import datetime

from app.schemas.base.base_model import ApiBaseModel

class WorkFilter(ApiBaseModel):
    Provider: str | None = None
    OriginalId: str | None = None
    Company: str | None = None
    Name: str | None = None
    Description: str | None = None
    Salary: int | None = None
    Remote: int | None = None

    CreatedFrom: datetime | None = None
    CreatedTo: datetime | None = None
    DeletedFrom: datetime | None = None
    DeletedTo: datetime | None = None

    Active: bool | None = None
    Application: bool | None = None
