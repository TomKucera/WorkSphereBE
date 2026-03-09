from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.auth import get_current_user

from app.application_processing.config.providers import PROVIDER_SETTINGS
from app.application_processing.providers.provider_registry import ProviderRegistry

from app.application_processing.domain.application_data import ApplicationData
from app.application_processing.domain.cv_payload import CvPayload

from app.db.repositories.work_application_repository import WorkApplicationRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.user_contact_repository import UserContactRepository
from app.db.repositories.cv_repository import CvRepository
from app.db.repositories.work_repository import WorkRepository

from app.schemas.users.work_application_list_query import WorkApplicationListQuery
from app.schemas.users.work_application_list_item import WorkApplicationListItem

from app.schemas.users.work_application import (
    WorkApplicationCreate,
    WorkApplicationUpdate,
    WorkApplicationResponse,
)

from app.schemas.base.page import Page

router = APIRouter(prefix="/applications", tags=["Work Applications"])


@router.get("", response_model=list[WorkApplicationResponse])
def list(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WorkApplicationRepository(db)
    return repo.list_by_user(user_id)

@router.get("/by-work/{work_id}", response_model=WorkApplicationResponse)
async def get_application_by_work(
    work_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns application of current user for given work_id.
    """

    repo_application = WorkApplicationRepository(db)
    applications = repo_application.list_by_user_and_work_ids(user_id, [work_id])

    application = None if len(applications) != 1 else applications[0]

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application

# @router.get("", response_model=Page[WorkApplicationListItem])
# def list_applications(
#     query: WorkApplicationListQuery = Depends(),
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """
#     Returns paginated, sorted and filtered list of works.
#     """
#     repo = WorkApplicationRepository(db)

#     items, total = repo.list(user_id, query)

#     return Page(
#         items=items,
#         page=query.page,
#         page_size=query.page_size,
#         total=total,
#     )

@router.post("/list", response_model=Page[WorkApplicationListItem])
def list_advanced(
    data: WorkApplicationListQuery,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns paginated, sorted and filtered list of works.
    """
    repo = WorkApplicationRepository(db)

    items, total = repo.list(user_id, data)

    return Page(
        Items=items,
        Page=data.Page,
        PageSize=data.PageSize,
        Total=total,
    )


@router.get("/{application_id}", response_model=WorkApplicationResponse)
def get_application(
    application_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WorkApplicationRepository(db)
    app = repo.get(application_id)

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return app


# @router.post("", response_model=WorkApplicationResponse)
# def create_application(
#     data: WorkApplicationCreate,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     cv_repo = CvRepository(db)
#     contact_repo = UserContactRepository(db)
#     application_repo = WorkApplicationRepository(db)
#     work_repo = WorkRepository(db)

#     print('data', data)

#     # Check work
#     work = work_repo.get(data.WorkId)
#     if not work:
#         raise HTTPException(status_code=400, detail="Invalid WorkId")
    
#     if work and work.RemovedByScanId:
#         raise HTTPException(status_code=400, detail="Work is not active")
        
#     # Check duplicate (UserId + WorkId)
#     existing = application_repo.get_by_user_and_work(user_id, data.WorkId)
#     if existing:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Application already exists for this work",
#         )

#     # Check CV
#     cv = cv_repo.get(data.CvId, user_id)
#     if not cv:
#         raise HTTPException(status_code=400, detail="Invalid CvId")

#     # Check contact Email
#     email_contact = contact_repo.get(data.ContactEmailId, user_id)
#     if not email_contact or email_contact.Type != "Email":
#         raise HTTPException(status_code=400, detail="Invalid email contact")

#     # Check contact Phone
#     phone_contact = contact_repo.get(data.ContactPhoneId, user_id)
#     if not phone_contact or phone_contact.Type != "Phone":
#         raise HTTPException(status_code=400, detail="Invalid phone contact")

#     # Load user for name snapshot
#     user_repo = UserRepository(db)
#     user = user_repo.get(user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Create application with snapshot values
#     application = application_repo.create(
#         UserId=user_id,
#         WorkId=data.WorkId,
#         CvId=data.CvId,
#         FirstName=user.FirstName,
#         LastName=user.LastName,
#         Email=email_contact.Value,
#         Phone=phone_contact.Value,
#         Message=data.Message,
#         Status="SUBMITTED"
#     )

#     return application

@router.post("", response_model=WorkApplicationResponse)
def create_application(
    data: WorkApplicationCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cv_repo = CvRepository(db)
    contact_repo = UserContactRepository(db)
    application_repo = WorkApplicationRepository(db)
    work_repo = WorkRepository(db)

    # ------------------------------------------------
    # Check work
    # ------------------------------------------------

    work = work_repo.get(data.WorkId)

    if not work:
        raise HTTPException(status_code=400, detail="Invalid WorkId")

    if work.RemovedByScanId:
        raise HTTPException(status_code=400, detail="Work is not active")

    # ------------------------------------------------
    # Duplicate
    # ------------------------------------------------

    existing = application_repo.get_by_user_and_work(user_id, data.WorkId)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application already exists for this work",
        )

    # ------------------------------------------------
    # CV
    # ------------------------------------------------

    cv = cv_repo.get(data.CvId, user_id)

    if not cv:
        raise HTTPException(status_code=400, detail="Invalid CvId")

    # ------------------------------------------------
    # Contacts
    # ------------------------------------------------

    email_contact = contact_repo.get(data.ContactEmailId, user_id)
    if not email_contact or email_contact.Type != "Email":
        raise HTTPException(status_code=400, detail="Invalid email contact")

    phone_contact = contact_repo.get(data.ContactPhoneId, user_id)
    if not phone_contact or phone_contact.Type != "Phone":
        raise HTTPException(status_code=400, detail="Invalid phone contact")

    # ------------------------------------------------
    # User snapshot
    # ------------------------------------------------

    user_repo = UserRepository(db)
    user = user_repo.get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ------------------------------------------------
    # AUTO APPLY
    # ------------------------------------------------

    if data.AutoApply:

        provider = work.Provider

        settings = PROVIDER_SETTINGS.get(provider)

        if not settings or not settings.auto_apply_enabled:
            raise HTTPException(
                status_code=400,
                detail=f"Auto apply not supported for provider {provider}",
            )

        provider_impl = ProviderRegistry.get(provider)

        cv_payload = CvPayload(
            filename=cv.OriginalFileName, # TODO: File name (on application or cv as ather name) !?
            mime_type=cv.ContentType,
            content=cv.FileContent,
        )

        application_data = ApplicationData(
            first_name=user.FirstName,
            last_name=user.LastName,
            email=email_contact.Value,
            phone=phone_contact.Value,
            message=data.Message,
            cv=cv_payload,
        )

        result = provider_impl.apply(work.OriginalId, work.Url, application_data)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "AUTO_APPLY_FAILED",
                    "provider": provider,
                    "message": result.error_message or "Automatic application failed",
                },
            )

    # ------------------------------------------------
    # SAVE APPLICATION (manual OR auto success)
    # ------------------------------------------------

    application = application_repo.create(
        UserId=user_id,
        WorkId=data.WorkId,
        CvId=data.CvId,
        FirstName=user.FirstName,
        LastName=user.LastName,
        Email=email_contact.Value,
        Phone=phone_contact.Value,
        Message=data.Message,
        Status="SUBMITTED",
        ApplicationType=  "AUTO" if data.AutoApply else "MANUAL"
    )

    return application


@router.put("/{application_id}", response_model=WorkApplicationResponse)
def update_application(
    application_id: int,
    data: WorkApplicationUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = WorkApplicationRepository(db)
    app = repo.get(application_id, user_id)

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = data.model_dump(exclude_unset=True)
    return repo.update(app, **update_data)
