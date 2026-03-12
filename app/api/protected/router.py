from fastapi import APIRouter, Depends
from app.core.auth import get_current_user

from app.api.protected.providers.routes import router as providers_router
from app.api.protected.integrations.gmail.routes import router as gmail_integration_router
from app.api.protected.integrations.inbox.routes import router as inbox_integration_router
from app.api.protected.ai.routes import router as ai_router
from app.api.protected.cvs.routes import router as cvs_router
from app.api.protected.scans.routes import router as scans_router
from app.api.protected.works.routes import router as works_router
from app.api.protected.user_contacts.routes import router as user_contacts_router
from app.api.protected.work_applications.routes import router as work_applications_router

protected_router = APIRouter(
    dependencies=[Depends(get_current_user)],
)

protected_router.include_router(providers_router)
protected_router.include_router(gmail_integration_router)
protected_router.include_router(inbox_integration_router)
protected_router.include_router(ai_router)
protected_router.include_router(cvs_router)
protected_router.include_router(scans_router)
protected_router.include_router(works_router)
protected_router.include_router(user_contacts_router)
protected_router.include_router(work_applications_router)
