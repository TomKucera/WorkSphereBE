from app.schemas.base.base_model import ApiBaseModel

class ScanOutputProvider(ApiBaseModel):
    AddedOriginalIds: list[str]
    RemovedOriginalIds: list[str]
    InvalidOriginalIds: list[str]