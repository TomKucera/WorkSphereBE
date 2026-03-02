from typing import List

from app.schemas.base.base_model import ApiBaseModel
from .generation_info import GenerationInfo

class CoverLetterResponse(ApiBaseModel):
    job_description: str
    cv_text: str
    body: str
    match_score: float
    job_skills: List[str]
    cv_skills: List[str]
    generation_info: GenerationInfo
