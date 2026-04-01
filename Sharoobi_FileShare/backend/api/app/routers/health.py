from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.domain import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        project=settings.project_name,
        auth_mode="jwt-local-admin",
        database_backend=settings.database_url.split(":", maxsplit=1)[0],
    )
