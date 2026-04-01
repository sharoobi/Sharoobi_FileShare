import shutil
from pathlib import Path

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.models import AccessPolicy, Device, Job, Package, Share, User
from app.schemas.domain import DeviceSummary, JobSummary, PackageSummary, PolicySummary, ShareSummary
from app.services.host_bridge import default_smb_share_name


def list_shares(session: Session) -> list[ShareSummary]:
    shares = session.execute(
        select(Share).options(joinedload(Share.policy)).order_by(Share.name.asc())
    ).scalars().all()
    return [share_to_summary(share) for share in shares]


def list_policies(session: Session) -> list[PolicySummary]:
    policies = session.execute(select(AccessPolicy).order_by(AccessPolicy.name.asc())).scalars().all()
    return [PolicySummary.model_validate(policy) for policy in policies]


def list_packages(session: Session) -> list[PackageSummary]:
    packages = session.execute(
        select(Package).options(joinedload(Package.share)).order_by(Package.name.asc())
    ).scalars().all()
    return [
        PackageSummary(
            id=package.id,
            name=package.name,
            version=package.version,
            category=package.category,
            installer_type=package.installer_type,
            silent_supported=package.silent_supported,
            entry_path=package.entry_path,
            share_slug=package.share.slug,
            install_args=package.install_args,
            is_enabled=package.is_enabled,
        )
        for package in packages
    ]


def list_devices(session: Session) -> list[DeviceSummary]:
    devices = session.execute(select(Device).order_by(Device.hostname.asc())).scalars().all()
    jobs_by_host = active_jobs_by_host(session)
    return [
        DeviceSummary(
            id=device.id,
            hostname=device.hostname,
            ip_address=device.ip_address,
            state=device.state,
            profile=device.profile,
            device_type=device.device_type,
            last_seen_at=device.last_seen_at,
            agent_version=device.agent_version,
            active_job=jobs_by_host.get(device.hostname),
        )
        for device in devices
    ]


def list_jobs(session: Session) -> list[JobSummary]:
    jobs = session.execute(
        select(Job)
        .options(joinedload(Job.share), joinedload(Job.package))
        .order_by(Job.created_at.desc())
    ).scalars().all()
    return [
        JobSummary(
            id=job.id,
            name=job.name,
            job_type=job.job_type,
            target_selector=job.target_selector,
            state=job.state,
            queued=job.queued,
            succeeded=job.succeeded,
            failed=job.failed,
            share_name=job.share.name if job.share else None,
            package_name=job.package.name if job.package else None,
            last_message=job.last_message,
            created_at=job.created_at,
        )
        for job in jobs
    ]


def get_user_with_roles(session: Session, username: str) -> User | None:
    statement: Select[tuple[User]] = (
        select(User)
        .where(User.username == username)
        .options(joinedload(User.roles))
    )
    return session.execute(statement).unique().scalar_one_or_none()


def active_jobs_by_host(session: Session) -> dict[str, str]:
    jobs = session.execute(
        select(Job).where(Job.state.in_(["queued", "running", "ready"]))
    ).scalars().all()
    mapping: dict[str, str] = {}
    for job in jobs:
        if job.target_selector.startswith("host:"):
            mapping[job.target_selector.removeprefix("host:")] = job.name
    return mapping


def share_to_summary(share: Share) -> ShareSummary:
    capacity_gb = None
    used_gb = None
    access_state = "host-bridge-required"
    size_gb = None
    source = Path(share.source_path)

    if source.exists():
        access_state = "direct-access"
        try:
            usage = shutil.disk_usage(source if source.is_dir() else source.parent)
            capacity_gb = round(usage.total / (1024**3), 2)
            used_gb = round((usage.total - usage.free) / (1024**3), 2)
        except OSError:
            access_state = "path-visible-without-usage"
    elif source.parent.exists():
        access_state = "path-missing"

    if share.size_bytes is not None:
        size_gb = round(share.size_bytes / (1024**3), 2)

    return ShareSummary(
        id=share.id,
        slug=share.slug,
        name=share.name,
        source_path=share.source_path,
        access_mode=share.access_mode,
        publish_strategy=share.publish_strategy,
        smb_share_name=share.smb_share_name or default_smb_share_name(share.slug),
        allow_guest=share.allow_guest,
        expose_via_smb=share.expose_via_smb,
        expose_via_web=share.expose_via_web,
        is_enabled=share.is_enabled,
        policy_name=share.policy.name if share.policy else None,
        read_limit_mbps=share.policy.read_limit_mbps if share.policy else None,
        file_count=share.file_count,
        size_gb=size_gb,
        capacity_gb=capacity_gb,
        used_gb=used_gb,
        last_scanned_at=share.last_scanned_at,
        access_state=access_state,
        last_bridge_status=share.last_bridge_status,
        last_bridge_message=share.last_bridge_message,
        last_bridge_node=share.last_bridge_node,
        last_path_exists=share.last_path_exists,
        last_path_kind=share.last_path_kind,
        last_smb_published=share.last_smb_published,
        notes=share.notes,
    )
