from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.deps import AuthContext, require_permissions
from app.schemas.domain import OverviewResponse
from app.services.queries import list_devices, list_jobs, list_packages, list_policies, list_shares

router = APIRouter(prefix="/api", tags=["overview"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview(
    _: AuthContext = Depends(require_permissions("system:read")),
    session: Session = Depends(get_session),
) -> OverviewResponse:
    settings = get_settings()
    return OverviewResponse(
        project_name=settings.project_name,
        status="db-persistent",
        auth_mode="jwt-local-admin",
        shares=list_shares(session),
        devices=list_devices(session),
        jobs=list_jobs(session),
        policies=list_policies(session),
        packages=list_packages(session),
    )
