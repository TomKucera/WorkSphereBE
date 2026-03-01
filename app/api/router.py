from fastapi import APIRouter
from app.api.public.router import public_router
from app.api.protected.router import protected_router

api_router = APIRouter(prefix="/api/v1")


api_router.include_router(public_router)
api_router.include_router(protected_router)
