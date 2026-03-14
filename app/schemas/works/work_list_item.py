from app.schemas.base.base_model import ApiBaseModel

from app.schemas.scans.scan_list_item_nested import (
    ScanListItemNested
)

from app.schemas.users.work_application_list_item_nested import (
    WorkApplicationListItemNested
)

class WorkListItem(ApiBaseModel):
    Id: int
    Provider: str
    OriginalId: str
    Name: str
    Description: str
    Url: str
    Company: str
    AddedByScanId: int
    RemovedByScanId: int | None
    RemoteRatio: int | None
    SalaryCurrency: str | None
    SalaryMax: int | None
    SalaryMin: int | None

    AddedByScan: ScanListItemNested
    RemovedByScan: ScanListItemNested | None

    Application: WorkApplicationListItemNested | None
    HasCustomDescription: bool
    MarkedForLater: bool

    class Config:
        from_attributes = True
