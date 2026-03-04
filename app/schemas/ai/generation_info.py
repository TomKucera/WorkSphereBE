from app.schemas.base.base_model import ApiBaseModel

class GenerationInfo(ApiBaseModel):
    Model: str
    Language: str
    LanguageLevel: str | None
    InputTokens: int
    OutputTokens: int
    EstimatedCostUsd: float
