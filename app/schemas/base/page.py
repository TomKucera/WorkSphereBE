from typing import Generic, List, TypeVar
from app.schemas.base.base_model import ApiBaseModel

T = TypeVar("T")

class Page(ApiBaseModel, Generic[T]):
    """
    Generic paged response.
    Used across the entire API for list endpoints.
    """

    Items: List[T]
    Page: int
    PageSize: int
    Total: int

    @property
    def TotalPages(self) -> int:
        """
        Computed number of pages.
        Not serialized automatically, but useful in Python code.
        """
        if self.PageSize == 0:
            return 0
        return (self.Total + self.PageSize - 1) // self.PageSize
