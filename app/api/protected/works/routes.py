from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.db.repositories.work_repository import WorkRepository
from app.db.repositories.work_application_repository import WorkApplicationRepository
from app.services.cv_matching_service import CvMatchingService
from app.schemas.base.page import Page
from app.db.models.work_application import WorkApplication

from app.schemas.works.work_detail import WorkDetail
from app.schemas.works.work_list_query import WorkListQuery
from app.schemas.works.work_list_item import WorkListItem
from app.schemas.users.work_application_list_item_nested import WorkApplicationListItemNested


router = APIRouter(
    prefix="/works",
    tags=["Works"],
)

# @router.get("", response_model=list[WorkRead])
# def list_works(
#     limit: int = 50,
#     db: Session = Depends(get_db),
# ):
#     repo = WorkRepository(db)
#     return repo.list(limit)


# @router.get("", response_model=Page[WorkListItem])
# def list_works(
#     query: WorkListQuery = Depends(),
#     db: Session = Depends(get_db),
# ):
#     """
#     Returns paginated, sorted and filtered list of works.
#     """
#     repo = WorkRepository(db)

#     items, total = repo.list(query)

#     return Page(
#         Items=items,
#         Page=query.Page,
#         PageSize=query.PageSize,
#         Total=total,
#     )

@router.post("/list", response_model=Page[WorkListItem])
def list_applications(
    data: WorkListQuery,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns paginated, sorted and filtered list of works.
    """
    repo_work = WorkRepository(db)
    repo_application = WorkApplicationRepository(db)

    items, total = repo_work.list(user_id, data)

    work_ids = [w.Id for w in items]
    applications = repo_application.list_by_user_and_work_ids(user_id, work_ids)
    apps_by_work_id: dict[int, WorkApplication] = { a.WorkId: a for a in applications}

    for i in items:
        app: WorkApplication = apps_by_work_id.get(i.Id)
        i.Application = None if app is None else WorkApplicationListItemNested.model_validate(app) # WorkApplicationListItemNested(Id=app.Id, Status=app.Status, CreatedAt=app.CreatedAt,UpdatedAt=app.UpdatedAt)

    return Page(
        Items=items,
        Page=data.Page,
        PageSize=data.PageSize,
        Total=total,
    )


@router.get("/{work_id}", response_model=WorkDetail)
def get_work(
    work_id: int,
    db: Session = Depends(get_db),
):
    repo = WorkRepository(db)
    work = repo.get(work_id)

    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    return work

@router.get("/provider/{provider}", response_model=list[WorkDetail])
def list_works_by_provider(
    provider: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    repo = WorkRepository(db)
    return repo.list_by_provider(provider, limit)

@router.get("/scan/{scan_id}", response_model=list[WorkDetail])
def list_works_by_scan(
    scan_id: int,
    db: Session = Depends(get_db),
):
    repo = WorkRepository(db)
    return repo.list_by_scan(scan_id)

@router.post("/{work_id}/match-cvs")
def match_cvs(
    work_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    service = CvMatchingService(db)
    return service.match(user_id, work_id)

