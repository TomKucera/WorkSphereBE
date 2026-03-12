from fastapi import APIRouter
from app.api.public.auth.routes import router as auth_router
from app.api.public.integrations.gmail.routes import router as gmail_integration_router

public_router = APIRouter()

public_router.include_router(auth_router)
public_router.include_router(gmail_integration_router)
