from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.deps import AuthContext, require_permissions
from app.schemas.agent import (
    AgentHeartbeatRequest,
    AgentHeartbeatResponse,
    AgentJobManifest,
    AgentJobStatusRequest,
    AgentJobStatusResponse,
)
from app.services.agent_runtime import get_next_agent_job, update_job_status, upsert_agent_device

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/heartbeat", response_model=AgentHeartbeatResponse)
def heartbeat(
    payload: AgentHeartbeatRequest,
    _: AuthContext = Depends(require_permissions("devices:write")),
    session: Session = Depends(get_session),
) -> AgentHeartbeatResponse:
    upsert_agent_device(
        session,
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        mac_address=payload.mac_address,
        profile=payload.profile,
        agent_version=payload.agent_version,
        notes=payload.notes,
    )
    return AgentHeartbeatResponse(
        hostname=payload.hostname,
        accepted=True,
        next_poll_seconds=20,
    )


@router.get("/jobs/next", response_model=AgentJobManifest | None)
def next_job(
    hostname: str,
    profile: str = "guest",
    _: AuthContext = Depends(require_permissions("jobs:read")),
    session: Session = Depends(get_session),
) -> AgentJobManifest | None:
    return get_next_agent_job(session, hostname, profile)


@router.post("/jobs/{job_id}/status", response_model=AgentJobStatusResponse)
def set_job_status(
    job_id: int,
    payload: AgentJobStatusRequest,
    _: AuthContext = Depends(require_permissions("jobs:write")),
    session: Session = Depends(get_session),
) -> AgentJobManifest | None:
    job = update_job_status(
        session,
        job_id=job_id,
        state=payload.state,
        message=payload.message,
        succeeded=payload.succeeded,
        failed=payload.failed,
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    return AgentJobStatusResponse(
        job_id=job.id,
        state=job.state,
        accepted=True,
    )
