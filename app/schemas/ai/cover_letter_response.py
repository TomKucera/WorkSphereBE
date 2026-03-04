from typing import List

from app.schemas.base.base_model import ApiBaseModel
from .generation_info import GenerationInfo

class CoverLetterResponse(ApiBaseModel):
    JobDescription: str
    CvText: str
    Body: str
    MatchScore: float
    JobSkills: List[str]
    CvSkills: List[str]
    # GenerationInfo: GenerationInfo
