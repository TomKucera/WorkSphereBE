from pydantic import constr
from typing import Literal

from app.schemas.base.base_model import ApiBaseModel


ContactType = Literal["Email", "Phone"]


class UserContactCreate(ApiBaseModel):
    Type: ContactType
    Value: constr(min_length=1, max_length=100) # type: ignore
    IsPrimary: bool = False


class UserContactUpdate(ApiBaseModel):
    Value: constr(min_length=1, max_length=100) | None = None # type: ignore
    IsPrimary: bool | None = None


class UserContactResponse(ApiBaseModel):
    Id: int
    Type: str
    Value: str
    IsPrimary: bool

    class Config:
        from_attributes = True