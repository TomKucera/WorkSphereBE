from fastapi import APIRouter

from app.application_processing.config.providers import PROVIDER_SETTINGS

from app.schemas.providers.provider_settings import ProviderSettingsResponse


router = APIRouter(prefix="/providers", tags=["Providers"])

@router.get("/settings", response_model=dict[str, ProviderSettingsResponse])
def get_provider_settings():

    return PROVIDER_SETTINGS