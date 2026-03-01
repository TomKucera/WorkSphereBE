from pydantic import Field
from app.schemas.base.base_model import ApiBaseModel

class Sorting(ApiBaseModel):
    SortColumn: str = "Id"
    SortOrder: str = Field("desc", pattern="^(asc|desc)$")
