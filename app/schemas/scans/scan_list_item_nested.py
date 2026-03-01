from datetime import datetime
from app.schemas.base.base_model import ApiBaseModel

from .scan_output import ScanOutput

class ScanListItemNested(ApiBaseModel):
    StartedAt: datetime
    EndedAt: datetime | None
