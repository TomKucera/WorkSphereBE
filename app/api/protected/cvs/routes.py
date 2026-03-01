import json

from fastapi import APIRouter, UploadFile, HTTPException, status, File, Depends, Form

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from io import BytesIO

from app.db.deps import get_db
from app.core.auth import get_current_user

from app.db.repositories.cv_repository import CvRepository
from app.db.repositories.cv_rag_repository import CvRagRepository

from app.schemas.cvs.cv import CvRead
from app.schemas.cvs.cv_update_active import CvUpdateActive
from app.schemas.cvs.cv_list_item import CvListItem
from app.schemas.cvs.cv_list_query import CvListQuery

from app.services.file_text_extractor import extract_text
from app.services.cv_rag_service import CvRagService

from app.schemas.base.page import Page

# from app.services.openai_embeddings import get_embedding
# from app.rag.search import score_cv
# from app.schemas.cvs.cv_match import (
#     CvMatchRequest,
#     CvMatchResponse,
#     CvMatchResult,
# )


router = APIRouter(prefix="/cvs", tags=["CVs"])

@router.get("", response_model=list[CvListItem])
def list_cvs(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CvRepository(db)
    return repo.get_by_user(user_id, active=True)

@router.post("/list", response_model=Page[CvListItem])
def list_applications(
    data: CvListQuery,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns paginated, sorted and filtered list of works.
    """
    repo = CvRepository(db)

    items, total = repo.list(user_id, data)

    return Page(
        Items=items,
        Page=data.Page,
        PageSize=data.PageSize,
        Total=total,
    )

@router.get("/{cv_id}", response_model=CvRead)
def get_cv(
    cv_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CvRepository(db)
    cv = repo.get(cv_id, user_id)

    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return cv

@router.get("/{cv_id}/file")
async def get_cv_file(
    cv_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CvRepository(db)
    cv = repo.get(cv_id, user_id)
    return StreamingResponse(
        BytesIO(cv.FileContent),
        # media_type="application/pdf",
        media_type=cv.ContentType,
        headers={
            "Content-Disposition": f'inline; filename="{cv.OriginalFileName}"'
        }
    )

@router.post("", response_model=CvRead)
async def create_cv(
    file: UploadFile = File(...),
    name: str = Form(...),
    note: str | None = Form(None),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await file.read()

    try:
        extracted_text = extract_text(content, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {e}")

    repo = CvRepository(db)

    # Check duplicate name and file name (UserId + Name/FileName)
    user_cvs = repo.get_by_user(user_id, active=None)

    existing_cv_by_name = next((cv for cv in user_cvs if cv.Name.lower() == name.lower()), None)
    if existing_cv_by_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CV already exists for this name",
        )
    
    existing_cv_by_file_name = next((cv for cv in user_cvs if cv.OriginalFileName.lower() == file.filename.lower()), None)
    if existing_cv_by_file_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CV already exists for this file name",
        )

    cv = repo.create(
        UserId=user_id,
        Name=name,
        Note=note,
        OriginalFileName=file.filename,
        ContentType=file.content_type,
        FileContent=content,
        ExtractedText=extracted_text,
        Active=True,
    )

    return cv

from fastapi import Path

@router.patch("/{cv_id}/active", response_model=CvRead)
def set_cv_active(
    cv_id: int = Path(...),
    data: CvUpdateActive = None,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CvRepository(db)

    cv = repo.set_active(user_id, cv_id, data.active)

    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return cv

@router.put("/{cv_id}", response_model=CvRead)
def update_cv(
    cv_id: int,
    language: str | None = None,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CvRepository(db)
    cv = repo.get(cv_id, user_id)

    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return repo.update(cv, language=language)


# @router.delete("/{cv_id}")
# def delete_cv(
#     cv_id: int,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     repo = CvRepository(db)
#     cv = repo.get(cv_id, user_id)

#     if not cv:
#         raise HTTPException(status_code=404, detail="CV not found")

#     repo.soft_delete(cv)
#     return {"ok": True}


@router.post("/{cv_id}/rag")
def build_cv_rag(
    cv_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cv_repo = CvRepository(db)
    cv = cv_repo.get(cv_id, user_id)

    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if not cv.ExtractedText:
        raise HTTPException(status_code=400, detail="CV has no extracted text")

    rag_repo = CvRagRepository(db)
    rag_service = CvRagService(rag_repo)

    rag_service.build_rag(cv_id=cv.Id, extracted_text=cv.ExtractedText)

    return {"status": "ok", "cv_id": cv.Id}


# TODO: add PATCH to update name, note ?!
# TODO: improve list (filter deleted, all), add actions: edit, activate


# @router.post("/match", response_model=CvMatchResponse)
# def match_cvs(
#     request: CvMatchRequest,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     cv_repo = CvRepository(db)
#     rag_repo = CvRagRepository(db)

#     job_embedding = get_embedding(request.job_text)
#     job_language = "en"

#     cvs = cv_repo.list_by_user(current_user.id)

#     if not cvs:
#         return CvMatchResponse(job_language=job_language, results=[])

#     cv_ids = [cv.id for cv in cvs]

#     cv_rags = rag_repo.get_by_cv_ids(cv_ids)

#     # Přemapování do dict pro O(1) lookup
#     rag_map = {rag.cv_id: rag for rag in cv_rags}

#     results = []

#     for cv in cvs:
#         cv_rag = rag_map.get(cv.id)
#         if not cv_rag:
#             continue

#         rag_data = json.loads(cv_rag.rag_data_json)
#         chunks = rag_data.get("chunks", [])

#         similarity, language_bonus, final_score = score_cv(
#             job_embedding=job_embedding,
#             chunks=chunks,
#             cv_language=cv.language,
#             job_language=job_language,
#         )

#         results.append(
#             CvMatchResult(
#                 cv_id=cv.id,
#                 file_name=cv.file_name,
#                 similarity=round(similarity, 4),
#                 language_bonus=round(language_bonus, 4),
#                 final_score=round(final_score, 4),
#                 match_percent=int(final_score * 100),
#             )
#         )

#     results.sort(key=lambda x: x.final_score, reverse=True)

#     return CvMatchResponse(
#         job_language=job_language,
#         results=results,
#     )
