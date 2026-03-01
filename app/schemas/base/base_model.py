from pydantic import BaseModel


def to_camel(string: str) -> str:
    return string[0].lower() + string[1:]


class ApiBaseModel(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
