from app.schemas.base.base_model import ApiBaseModel

class WorkListItemNested(ApiBaseModel):
    Id: int
    Provider: str
    OriginalId: str
    Name: str
    Url: str
    Company: str
    AddedByScanId: int
    RemovedByScanId: int | None

    class Config:
        from_attributes = True
