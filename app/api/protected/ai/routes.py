from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.services.scraping_service import ScrapingService
from app.services.ai.cover_letter_service import CoverLetterService
from app.services.ai.language import Language, LanguageLevel

from app.db.repositories.work_repository import WorkRepository
from app.db.repositories.cv_repository import CvRepository

from app.schemas.ai.cover_letter_response import CoverLetterResponse

from app.db.deps import get_db
from app.core.auth import get_current_user


router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/cover-letter", response_model=CoverLetterResponse)
def generate_cover_letter(
    work_id: int = Query(...),
    cv_id: int = Query(...),
    language: Language = Query(Language.cs),
    language_level: LanguageLevel | None = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """
    Generate AI cover letter for given work and CV.
    """

    # max_chars: int = Query(1200, ge=300, le=3000),
    max_chars: int = 1000 # TODO: read from provider settings

    work_repo = WorkRepository(db)
    cv_repo = CvRepository(db)
 
    # validate inputs
    work = work_repo.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    
    if not len(work.Description):
        raise HTTPException(status_code=422, detail="Work has no description and cannot be used for generation")

    cv = cv_repo.get(cv_id, user_id, active=None)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    if not cv.Active:
        raise HTTPException(status_code=409, detail="CV is inactive and cannot be used for generation")
    
    job_description = ScrapingService.strip_html(work.Description)
    cv_text = cv.ExtractedText

    service = CoverLetterService()

    result = service.generate(
        job_description=job_description,
        cv_text=cv_text,
        max_chars=max_chars,
        language=language.value,
        language_level=language_level.value if language_level else None,
    )

    return CoverLetterResponse(
        job_description=job_description,
        cv_text=cv_text,
        body=result["body"],
        match_score=result["match_score"],
        job_skills=result["job_skills"],
        cv_skills=result["cv_skills"],
        generation_info=result["generation_info"],
    )