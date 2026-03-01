from datetime import datetime

from app.schemas.base.base_model import ApiBaseModel

class WorkDetail(ApiBaseModel):
    Id: int
    Provider: str
    OriginalId: str
    Name: str
    Description: str
    Url: str
    Company: str
    MainArea: str
    Collaborations: str
    Areas: str
    Seniorities: str
    AddedByScanId: int
    RemovedByScanId: int | None
    ValidFrom: datetime
    ValidTo: datetime
    SnapshotFileName: str | None
    RemoteRatio: int | None
    SalaryCurrency: str | None
    SalaryMax: int | None
    SalaryMin: int | None

    class Config:
        from_attributes = True
