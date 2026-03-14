from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.services.cv_matching_service import CvMatchingService
from app.services.scraping_service import ScrapingService

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.db.repositories.work_repository import WorkRepository
from app.db.repositories.work_bookmark_repository import WorkBookmarkRepository
from app.db.repositories.work_application_repository import WorkApplicationRepository

from app.schemas.base.page import Page
from app.db.models.work_application import WorkApplication
from app.db.models.work_description import WorkDescription

from app.schemas.works.work_description_upsert_request import WorkDescriptionUpsertRequest
from app.schemas.works.work_bookmark_update import WorkBookmarkUpdate
from app.schemas.works.work_detail import WorkDetail
from app.schemas.works.work_list_query import WorkListQuery
from app.schemas.works.work_list_item import WorkListItem
from app.schemas.users.work_application_list_item_nested import WorkApplicationListItemNested
from app.schemas.works.work_scrape_response import WorkScrapeResponse


router = APIRouter(
    prefix="/works",
    tags=["Works"],
)

@router.get("/{work_id}/description", response_model=str)
def get_work_description(
    work_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    work_repo = WorkRepository(db)

    # Check work existence
    work = work_repo.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    entity = work_repo.get_work_description(user_id, work_id)

    if not entity:
        raise HTTPException(status_code=404, detail="Description override not found")

    return entity.Description

@router.put("/{work_id}/description", status_code=204)
def upsert_work_description(
    work_id: int,
    data: WorkDescriptionUpsertRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo_work = WorkRepository(db)
    repo_application = WorkApplicationRepository(db)

    work = repo_work.get(work_id)
    if not work:
        raise HTTPException(status_code=400, detail="Invalid WorkId")

    if work.RemovedByScanId:
        raise HTTPException(status_code=400, detail="Work is not active")
    
    # Check application (UserId + WorkId)
    application = repo_application.get_by_user_and_work(user_id, work_id)
    if application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot modify description after application has been submitted"
        )

    repo_work.upsert_work_description(user_id=user_id, work_id=work_id, description=data.Description)

    return Response(status_code=204)

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
def list_advanced(
    data: WorkListQuery,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns paginated, sorted and filtered list of works.
    """
    repo_work = WorkRepository(db)
    repo_bookmark = WorkBookmarkRepository(db)
    repo_application = WorkApplicationRepository(db)

    items, total = repo_work.list(user_id, data)

    work_ids = [w.Id for w in items]
    applications = repo_application.list_by_user_and_work_ids(user_id, work_ids)
    descriptions = repo_work.get_work_descriptions_by_work_ids(user_id, work_ids)
    bookmarked_work_ids = repo_bookmark.list_marked_work_ids(user_id, work_ids)

    apps_by_work_id: dict[int, WorkApplication] = { a.WorkId: a for a in applications}
    descriptions_by_work_id: dict[int, WorkDescription] = { d.WorkId: d for d in descriptions}

    for i in items:
        app: WorkApplication = apps_by_work_id.get(i.Id)
        description: WorkDescription = descriptions_by_work_id.get(i.Id)
        i.Application = None if app is None else WorkApplicationListItemNested.model_validate(app)
        i.HasCustomDescription = description is not None
        i.MarkedForLater = i.Id in bookmarked_work_ids


    return Page(
        Items=items,
        Page=data.Page,
        PageSize=data.PageSize,
        Total=total,
    )


@router.get("/{work_id}", response_model=WorkDetail)
def get_work(
    work_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WorkRepository(db)
    repo_bookmark = WorkBookmarkRepository(db)
    work = repo.get(work_id)

    # work.Description = "Hledáme spolehlivého, pracovitého, ale také pohodového kolegu/kolegyni se smyslem pro humor, který/á se rád věnuje IT.\nPožadujeme znalost Python a jeho frameworku Django / Django Rest Framework.\nNáplní práce nového kolegy/ně bude:\nVedení juniorních backend vývojářů (Django, Django Rest Framework)\nKomunikace s kolegy\nPráce s Gitem\nCodereview\nNávrh řešení backendu aplikací\nVývoj složitých částí backendu v Djangu / Django Rest Frameworku nebo FastAPI\nNa jak dlouho?\nJe možnost pracovat per-project\nJe možné spolupracovat dlouhodobě\nKomu by mohla tato pozice vyhovovat?\nNěkdo, kdo má své zakázky, ale rád by souběžně vyzkoušel i práci v agentuře\nNěkdo, kdo chce změnu oproti korporátu\nNěkdo, kdo si chce šáhnout na vývoj pomocí moderních technologií(Django 3, FastAPI)\nNaše firemní kultura:\nInovativnost - Nové technologie, otevřenost návrhům a změnám\nPřátelské pracovní prostředí - Otevřená komunikace, důvěrné vztahy, pivo s ředitelem, neformálnost\nFairplay - Ve firmě i mimo ni, spokojenost zaměstnanců, spokojenost klientů, transparentnost\nProaktivita - Realizace vlastních nápadů, angažovanost\nFlexibilita - Otevřená/nestriktní pravidla, home office"

#     work.Description = """
# <div class=\"wysiwyg-content pt-20\"><p>Hledáme spolehlivého, pracovitého, ale také pohodového kolegu/kolegyni se smyslem pro humor, který/á se rád věnuje IT. </p>\n<p>Požadujeme znalost Python a jeho frameworku Django / Django Rest Framework.</p>\n<p>Náplní práce nového kolegy/ně bude:</p>\n<ul>\n<li>Vedení juniorních backend vývojářů (Django, Django Rest Framework)</li>\n<li>Komunikace s kolegy</li>\n<li>Práce s Gitem</li>\n<li>Codereview</li>\n<li>Návrh řešení backendu aplikací</li>\n<li>Vývoj složitých částí backendu v Djangu / Django Rest Frameworku nebo FastAPI</li>\n</ul>\n<p><span>Na jak dlouho?</span></p>\n<ul>\n<li><span>Je možnost pracovat per-project</span></li>\n<li><span>Je možné spolupracovat dlouhodobě<br/></span></li>\n</ul>\n<p><span>Komu by mohla tato pozice vyhovovat?</span></p>\n<ul>\n<li><span>Někdo, kdo má své zakázky, ale rád by souběžně vyzkoušel i práci v agentuře</span></li>\n<li><span>Někdo, kdo chce změnu oproti korporátu</span></li>\n<li><span>Někdo, kdo si chce šáhnout na vývoj pomocí moderních technologií(Django 3, FastAPI)</span></li>\n</ul>\n<p>Naše firemní kultura:</p>\n<ul>\n<li>Inovativnost - Nové technologie, otevřenost návrhům a změnám</li>\n<li>Přátelské pracovní prostředí - Otevřená komunikace, důvěrné vztahy, pivo s ředitelem, neformálnost</li>\n<li>Fairplay - Ve firmě i mimo ni, spokojenost zaměstnanců, spokojenost klientů, transparentnost</li>\n<li>Proaktivita - Realizace vlastních nápadů, angažovanost</li>\n<li>Flexibilita - Otevřená/nestriktní pravidla, home office</li>\n</ul></div>
#     """

    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    work.MarkedForLater = repo_bookmark.is_marked(user_id, work_id)
    return work


@router.patch("/{work_id}/mark-for-later", status_code=204)
def set_work_marked_for_later(
    work_id: int,
    data: WorkBookmarkUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo_work = WorkRepository(db)
    repo_bookmark = WorkBookmarkRepository(db)

    work = repo_work.get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    if data.MarkedForLater:
        if not repo_bookmark.is_marked(user_id, work_id):
            repo_bookmark.create(user_id, work_id)
    else:
        repo_bookmark.delete(user_id, work_id)

    return Response(status_code=204)

@router.get("/{work_id}/scrape", response_model=WorkScrapeResponse)
def scrape_work(
    work_id: int,
    format: Literal["plain", "html"] = Query("plain"),
    db: Session = Depends(get_db),
):
    repo = WorkRepository(db)
    work = repo.get(work_id)

    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    service = ScrapingService()

    result = service.scrape_work_text(work, format=format)

    if not result:
        raise HTTPException(status_code=400, detail="Unable to scrape job description")

    return WorkScrapeResponse(
        WorkId=work.Id,
        Format=format,
        Content=result,
    )

@router.get("/provider/{provider}", response_model=list[WorkDetail])
def list_works_by_provider(
    provider: str,
    limit: int = 50,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WorkRepository(db)
    repo_bookmark = WorkBookmarkRepository(db)
    items = repo.list_by_provider(provider, limit)
    bookmarked_work_ids = repo_bookmark.list_marked_work_ids(user_id, [item.Id for item in items])
    for item in items:
        item.MarkedForLater = item.Id in bookmarked_work_ids
    return items

@router.get("/scan/{scan_id}", response_model=list[WorkDetail])
def list_works_by_scan(
    scan_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WorkRepository(db)
    repo_bookmark = WorkBookmarkRepository(db)
    items = repo.list_by_scan(scan_id)
    bookmarked_work_ids = repo_bookmark.list_marked_work_ids(user_id, [item.Id for item in items])
    for item in items:
        item.MarkedForLater = item.Id in bookmarked_work_ids
    return items

@router.post("/{work_id}/match-cvs")
def match_cvs(
    work_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    service = CvMatchingService(db)
    return service.match(user_id, work_id)
