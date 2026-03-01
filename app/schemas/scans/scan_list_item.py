from datetime import datetime
from app.schemas.base.base_model import ApiBaseModel

from .scan_output import ScanOutput

class ScanInput(ApiBaseModel):
    Providers: list[str]

class ScanListItem(ApiBaseModel):
    Id: int
    Input: ScanInput
    Output: ScanOutput | None
    StartedAt: datetime
    EndedAt: datetime | None
