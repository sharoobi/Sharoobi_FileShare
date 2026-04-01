from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.deps import AuthContext, require_permissions
from app.models import Package, Share
from app.schemas.domain import PackageCreate, PackageSummary
from app.services.queries import list_packages

router = APIRouter(prefix="/api/packages", tags=["packages"])


@router.get("", response_model=list[PackageSummary])
def get_packages(
    _: AuthContext = Depends(require_permissions("packages:read")),
    session: Session = Depends(get_session),
) -> list[PackageSummary]:
    return list_packages(session)


@router.post("", response_model=PackageSummary, status_code=status.HTTP_201_CREATED)
def create_package(
    payload: PackageCreate,
    _: AuthContext = Depends(require_permissions("packages:write")),
    session: Session = Depends(get_session),
) -> PackageSummary:
    share = session.scalar(select(Share).where(Share.slug == payload.share_slug))
    if share is None:
        raise HTTPException(status_code=404, detail="Share not found.")

    package = Package(
        name=payload.name,
        version=payload.version,
        category=payload.category,
        installer_type=payload.installer_type,
        silent_supported=payload.silent_supported,
        install_args=payload.install_args,
        entry_path=payload.entry_path,
        share_id=share.id,
        is_enabled=payload.is_enabled,
    )
    session.add(package)
    session.commit()
    created = next(item for item in list_packages(session) if item.id == package.id)
    return created
