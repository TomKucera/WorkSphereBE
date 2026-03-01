from typing import Generic, TypeVar

from app.schemas.base.base_model import ApiBaseModel
from app.schemas.base.paging import Paging
from app.schemas.base.sorting import Sorting

TFilter = TypeVar("TFilter", bound=ApiBaseModel)

class BaseListQuery(Paging, Sorting, Generic[TFilter]):
    filter: TFilter | None = None