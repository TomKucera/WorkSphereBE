from typing import Optional
from pydantic import Field
from app.schemas.base.base_model import ApiBaseModel

class ProviderSettingsResponse(ApiBaseModel):

    MaxMessageLength: Optional[int] = Field(alias="max_message_length")

    AutoApplyEnabled: bool = Field(alias="auto_apply_enabled")
