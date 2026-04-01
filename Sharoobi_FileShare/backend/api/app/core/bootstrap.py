from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import hash_password
from app.models import AccessPolicy, Device, Job, Package, Role, Share, User
from app.services.host_bridge import default_smb_share_name

ROLE_DEFINITIONS = [
    {
        "slug": "admin",
        "name": "Administrator",
        "description": "Full platform control across shares, devices, jobs, and policies.",
        "permissions": [
            "system:read",
            "shares:read",
            "shares:write",
            "policies:read",
            "policies:write",
            "packages:read",
            "packages:write",
            "devices:read",
            "devices:write",
            "jobs:read",
            "jobs:write",
            "auth:manage",
        ],
    },
    {
        "slug": "technician",
        "name": "Technician",
        "description": "Can browse approved shares, trigger jobs, and view device state.",
        "permissions": [
            "system:read",
            "shares:read",
            "packages:read",
            "devices:read",
            "jobs:read",
            "jobs:write",
        ],
    },
    {
        "slug": "viewer",
        "name": "Viewer",
        "description": "Read-only operational visibility.",
        "permissions": [
            "system:read",
            "shares:read",
            "packages:read",
            "devices:read",
            "jobs:read",
            "policies:read",
        ],
    },
]

POLICY_DEFINITIONS = [
    {
        "slug": "guest-browse",
        "name": "Guest Browse",
        "description": "Browse-only policy for temporary LAN guests.",
        "read_limit_mbps": 35,
        "install_only": False,
        "allow_download": True,
        "allow_browse": True,
        "allow_smb": True,
        "allow_web": True,
        "allow_guest": True,
        "concurrent_sessions": 3,
    },
    {
        "slug": "tech-fast-lan",
        "name": "Tech Fast LAN",
        "description": "High-throughput policy for technicians on trusted local networks.",
        "read_limit_mbps": 250,
        "install_only": False,
        "allow_download": True,
        "allow_browse": True,
        "allow_smb": True,
        "allow_web": True,
        "allow_guest": False,
        "concurrent_sessions": 12,
    },
    {
        "slug": "install-only",
        "name": "Install Only",
        "description": "Path is exposed through controlled jobs or agent execution only.",
        "read_limit_mbps": 90,
        "install_only": True,
        "allow_download": False,
        "allow_browse": False,
        "allow_smb": False,
        "allow_web": False,
        "allow_guest": False,
        "concurrent_sessions": 4,
    },
]


def seed_database(session: Session, settings: Settings) -> None:
    roles = seed_roles(session)
    policies = seed_policies(session)
    seed_admin_user(session, settings, roles["admin"])
    shares = seed_shares(session, settings, policies)
    seed_packages(session, shares)
    seed_devices(session)
    seed_jobs(session, shares)
    session.commit()


def seed_roles(session: Session) -> dict[str, Role]:
    current_roles = {
        role.slug: role
        for role in session.execute(select(Role)).scalars().all()
    }
    for definition in ROLE_DEFINITIONS:
        role = current_roles.get(definition["slug"])
        if role is None:
            role = Role(
                slug=definition["slug"],
                name=definition["name"],
                description=definition["description"],
                permissions=definition["permissions"],
            )
            session.add(role)
            current_roles[role.slug] = role
        else:
            role.name = definition["name"]
            role.description = definition["description"]
            role.permissions = definition["permissions"]
    session.flush()
    return current_roles


def seed_policies(session: Session) -> dict[str, AccessPolicy]:
    current_policies = {
        policy.slug: policy
        for policy in session.execute(select(AccessPolicy)).scalars().all()
    }
    for definition in POLICY_DEFINITIONS:
        policy = current_policies.get(definition["slug"])
        if policy is None:
            policy = AccessPolicy(**definition)
            session.add(policy)
            current_policies[policy.slug] = policy
        else:
            for key, value in definition.items():
                setattr(policy, key, value)
    session.flush()
    return current_policies


def seed_admin_user(session: Session, settings: Settings, admin_role: Role) -> None:
    admin = session.scalar(select(User).where(User.username == settings.bootstrap_admin_username))
    if admin is None:
        admin = User(
            username=settings.bootstrap_admin_username,
            full_name="Local Bootstrap Admin",
            password_hash=hash_password(settings.bootstrap_admin_password),
            is_active=True,
            is_superuser=True,
        )
        admin.roles.append(admin_role)
        session.add(admin)
        session.flush()


def seed_shares(
    session: Session,
    settings: Settings,
    policies: dict[str, AccessPolicy],
) -> dict[str, Share]:
    definitions = [
        {
            "slug": "main-storage",
            "name": "Main Shared Storage",
            "source_path": settings.primary_share_path,
            "access_mode": "browse-download",
            "publish_strategy": "hybrid",
            "allow_guest": False,
            "expose_via_smb": True,
            "expose_via_web": True,
            "policy_slug": "tech-fast-lan",
            "notes": "Top-level path for technician-driven browsing and controlled copy jobs.",
        },
        {
            "slug": "office-installers",
            "name": "Office Installers",
            "source_path": settings.office_share_path,
            "access_mode": "install-only",
            "publish_strategy": "agent-gated",
            "allow_guest": False,
            "expose_via_smb": False,
            "expose_via_web": False,
            "policy_slug": "install-only",
            "notes": "Used by the agent or controlled execution jobs instead of direct browsing.",
        },
        {
            "slug": "driver-archive",
            "name": "Driver Archive",
            "source_path": settings.driver_share_path,
            "access_mode": "browse-download",
            "publish_strategy": "lan-smb",
            "allow_guest": False,
            "expose_via_smb": True,
            "expose_via_web": True,
            "policy_slug": "tech-fast-lan",
            "notes": "Large driver repository optimized for fast LAN access.",
        },
    ]

    current_shares = {
        share.slug: share
        for share in session.execute(select(Share)).scalars().all()
    }
    for definition in definitions:
        policy_slug = definition["policy_slug"]
        payload = {
            key: value
            for key, value in definition.items()
            if key != "policy_slug"
        }
        payload["policy_id"] = policies[policy_slug].id
        payload["smb_share_name"] = default_smb_share_name(payload["slug"])
        share = current_shares.get(payload["slug"])
        if share is None:
            share = Share(**payload)
            session.add(share)
            current_shares[share.slug] = share
        else:
            for key, value in payload.items():
                setattr(share, key, value)
    session.flush()
    return current_shares


def seed_packages(session: Session, shares: dict[str, Share]) -> None:
    definitions = [
        {
            "name": "Microsoft Office 2024",
            "version": "2024",
            "category": "productivity",
            "installer_type": "folder",
            "silent_supported": True,
            "install_args": "/configure configuration.xml",
            "entry_path": ".",
            "share_slug": "office-installers",
        },
        {
            "name": "VMware Workstation Pro",
            "version": "17.5.2",
            "category": "virtualization",
            "installer_type": "folder",
            "silent_supported": True,
            "install_args": "/s /v/qn",
            "entry_path": "FaresCD.Com-VMware.Workstation.Pro.17.5.2_x64",
            "share_slug": "main-storage",
        },
        {
            "name": "Drivers Snapshot",
            "version": "current",
            "category": "drivers",
            "installer_type": "folder",
            "silent_supported": False,
            "install_args": "",
            "entry_path": ".",
            "share_slug": "driver-archive",
        },
    ]
    current_packages = {
        (package.name, package.share_id): package
        for package in session.execute(select(Package)).scalars().all()
    }
    for definition in definitions:
        share = shares[definition["share_slug"]]
        key = (definition["name"], share.id)
        package = current_packages.get(key)
        payload = {
            "name": definition["name"],
            "version": definition["version"],
            "category": definition["category"],
            "installer_type": definition["installer_type"],
            "silent_supported": definition["silent_supported"],
            "install_args": definition["install_args"],
            "entry_path": definition["entry_path"],
            "share_id": share.id,
            "is_enabled": True,
        }
        if package is None:
            session.add(Package(**payload))
        else:
            for attr, value in payload.items():
                setattr(package, attr, value)


def seed_devices(session: Session) -> None:
    if session.scalar(select(Device.id).limit(1)) is not None:
        return

    now = datetime.now(tz=UTC)
    session.add_all(
        [
            Device(
                hostname="TECH-BENCH-01",
                ip_address="192.168.246.21",
                mac_address="00-50-56-A8-11-21",
                state="online",
                profile="technician",
                device_type="client",
                agent_version="bridge-0.1.0",
                last_seen_at=now,
            ),
            Device(
                hostname="CLIENT-LAPTOP-04",
                ip_address="192.168.246.39",
                mac_address="34-17-EB-01-0A-8F",
                state="guest",
                profile="guest",
                device_type="client",
                agent_version=None,
                last_seen_at=now,
            ),
        ]
    )


def seed_jobs(session: Session, shares: dict[str, Share]) -> None:
    if session.scalar(select(Job.id).limit(1)) is not None:
        return

    session.add_all(
        [
            Job(
                name="Office 2024 controlled install",
                job_type="install",
                state="ready",
                target_selector="group:managed-office",
                queued=12,
                succeeded=0,
                failed=0,
                share_id=shares["office-installers"].id,
                last_message="Awaiting Windows agent rollout.",
            ),
            Job(
                name="Drivers fast mirror",
                job_type="copy",
                state="draft",
                target_selector="group:tech-benches",
                queued=6,
                succeeded=0,
                failed=0,
                share_id=shares["driver-archive"].id,
                last_message="SMB strategy not yet activated on Windows host.",
            ),
        ]
    )
