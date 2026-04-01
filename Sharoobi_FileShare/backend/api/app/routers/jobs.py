from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.deps import AuthContext, require_permissions
from app.models import Job, Package, Share
from app.schemas.domain import JobCreate, JobSummary
from app.services.queries import list_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=list[JobSummary])
def get_jobs(
    _: AuthContext = Depends(require_permissions("jobs:read")),
    session: Session = Depends(get_session),
) -> list[JobSummary]:
    return list_jobs(session)


@router.post("", response_model=JobSummary, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    _: AuthContext = Depends(require_permissions("jobs:write")),
    session: Session = Depends(get_session),
) -> JobSummary:
    share = None
    package = None
    if payload.share_slug:
        share = session.scalar(select(Share).where(Share.slug == payload.share_slug))
        if share is None:
            raise HTTPException(status_code=404, detail="Share not found.")
    if payload.package_id:
        package = session.get(Package, payload.package_id)
        if package is None:
            raise HTTPException(status_code=404, detail="Package not found.")

    job = Job(
        name=payload.name,
        job_type=payload.job_type,
        state="queued",
        target_selector=payload.target_selector,
        queued=payload.queued,
        last_message=payload.last_message,
        share_id=share.id if share else None,
        package_id=package.id if package else None,
    )
    session.add(job)
    session.commit()
    created = next(item for item in list_jobs(session) if item.id == job.id)
    return created
