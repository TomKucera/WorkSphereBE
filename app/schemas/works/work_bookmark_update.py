from app.schemas.base.base_model import ApiBaseModel


class WorkBookmarkUpdate(ApiBaseModel):
    MarkedForLater: bool
