from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Device, Job
from app.schemas.agent import AgentJobManifest


def upsert_agent_device(
    session: Session,
    *,
    hostname: str,
    ip_address: str,
    mac_address: str | None,
    profile: str,
    agent_version: str,
    notes: str,
) -> Device:
    device = session.scalar(select(Device).where(Device.hostname == hostname))
    if device is None:
        device = Device(hostname=hostname)
        session.add(device)

    device.ip_address = ip_address
    device.mac_address = mac_address
    device.profile = profile
    device.agent_version = agent_version
    device.device_type = "client-agent"
    device.state = "online"
    device.notes = notes
    device.last_seen_at = datetime.now(tz=UTC)
    session.commit()
    return device


def get_next_agent_job(session: Session, hostname: str, profile: str) -> AgentJobManifest | None:
    statement = (
        select(Job)
        .options(joinedload(Job.share), joinedload(Job.package))
        .where(
            Job.job_type == "install",
            Job.state.in_(["queued", "ready", "running"]),
            or_(
                Job.target_selector == f"host:{hostname}",
                Job.target_selector == f"group:{profile}",
                Job.target_selector == "all",
            ),
        )
        .order_by(Job.created_at.asc())
    )
    job = session.execute(statement).scalars().first()
    if job is None:
        return None

    return AgentJobManifest(
        job_id=job.id,
        job_name=job.name,
        job_type=job.job_type,
        share_slug=job.share.slug if job.share else None,
        share_path=job.share.source_path if job.share else None,
        package_name=job.package.name if job.package else None,
        package_version=job.package.version if job.package else None,
        entry_path=job.package.entry_path if job.package else None,
        installer_type=job.package.installer_type if job.package else None,
        install_args=job.package.install_args if job.package else None,
        silent_supported=job.package.silent_supported if job.package else False,
        target_selector=job.target_selector,
        issued_at=datetime.now(tz=UTC),
    )


def update_job_status(
    session: Session,
    *,
    job_id: int,
    state: str,
    message: str,
    succeeded: int | None,
    failed: int | None,
) -> Job | None:
    job = session.get(Job, job_id)
    if job is None:
        return None

    now = datetime.now(tz=UTC)
    if state == "running" and job.started_at is None:
        job.started_at = now
    if state in {"completed", "failed"}:
        job.finished_at = now

    job.state = state
    job.last_message = message
    if succeeded is not None:
        job.succeeded = succeeded
    if failed is not None:
        job.failed = failed

    session.commit()
    return job
