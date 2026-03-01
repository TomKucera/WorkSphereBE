from pydantic import Field
from app.schemas.base.base_model import ApiBaseModel

class Paging(ApiBaseModel):
    Page: int = Field(1, ge=1)
    PageSize: int = Field(20, ge=1, le=100)
