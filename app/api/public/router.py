from fastapi import APIRouter
from app.api.public.auth.routes import router as auth_router

public_router = APIRouter()

public_router.include_router(auth_router)
