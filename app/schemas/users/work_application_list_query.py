from app.schemas.base.base_list_query import BaseListQuery
from .work_application_filter import WorkApplicationFilter


class WorkApplicationListQuery(
    BaseListQuery[WorkApplicationFilter]
):
    pass