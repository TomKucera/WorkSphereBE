from app.schemas.base.base_list_query import BaseListQuery
from .work_filter import WorkFilter


class WorkListQuery(
    BaseListQuery[WorkFilter]
):
    pass