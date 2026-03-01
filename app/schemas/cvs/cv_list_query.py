from app.schemas.base.base_list_query import BaseListQuery
from .cv_filter import CvFilter

class CvListQuery(
    BaseListQuery[CvFilter]
):
    pass