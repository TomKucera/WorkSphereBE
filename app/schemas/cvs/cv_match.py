from typing import List
from app.schemas.base.base_model import ApiBaseModel


class CvMatchRequest(ApiBaseModel):
    job_text: str

class CvMatchResult(ApiBaseModel):
    cv_id: int
    file_name: str
    similarity: float
    language_bonus: float
    final_score: float
    match_percent: int


class CvMatchResponse(ApiBaseModel):
    job_language: str
    results: List[CvMatchResult]
