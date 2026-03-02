from app.schemas.base.base_model import ApiBaseModel

class GenerationInfo(ApiBaseModel):
    model: str
    language: str
    language_level: str | None
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
