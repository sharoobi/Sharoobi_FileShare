from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    project: str
    auth_mode: str
    database_backend: str


class ShareSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    source_path: str
    access_mode: str
    publish_strategy: str
    smb_share_name: str | None
    allow_guest: bool
    expose_via_smb: bool
    expose_via_web: bool
    is_enabled: bool
    policy_name: str | None
    read_limit_mbps: int | None
    file_count: int | None
    size_gb: float | None
    capacity_gb: float | None
    used_gb: float | None
    last_scanned_at: datetime | None
    access_state: str
    last_bridge_status: str | None
    last_bridge_message: str | None
    last_bridge_node: str | None
    last_path_exists: bool | None
    last_path_kind: str | None
    last_smb_published: bool | None
    notes: str


class DeviceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hostname: str
    ip_address: str
    state: str
    profile: str
    device_type: str
    last_seen_at: datetime | None
    agent_version: str | None = None
    active_job: str | None = None


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    job_type: str
    target_selector: str
    state: str
    queued: int
    succeeded: int
    failed: int
    share_name: str | None = None
    package_name: str | None = None
    last_message: str
    created_at: datetime


class PolicySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str
    read_limit_mbps: int
    install_only: bool
    allow_download: bool
    allow_browse: bool
    allow_smb: bool
    allow_web: bool
    allow_guest: bool
    concurrent_sessions: int


class PackageSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    category: str
    installer_type: str
    silent_supported: bool
    entry_path: str
    share_slug: str
    install_args: str
    is_enabled: bool


class ShareCreate(BaseModel):
    slug: str
    name: str
    source_path: str
    access_mode: str = "browse-download"
    publish_strategy: str = "hybrid"
    smb_share_name: str | None = None
    allow_guest: bool = False
    expose_via_smb: bool = True
    expose_via_web: bool = True
    is_enabled: bool = True
    policy_slug: str | None = None
    notes: str = ""


class ShareUpdate(BaseModel):
    name: str | None = None
    source_path: str | None = None
    access_mode: str | None = None
    publish_strategy: str | None = None
    smb_share_name: str | None = None
    allow_guest: bool | None = None
    expose_via_smb: bool | None = None
    expose_via_web: bool | None = None
    is_enabled: bool | None = None
    policy_slug: str | None = None
    notes: str | None = None


class PolicyCreate(BaseModel):
    slug: str
    name: str
    description: str = ""
    read_limit_mbps: int = 0
    install_only: bool = False
    allow_download: bool = True
    allow_browse: bool = True
    allow_smb: bool = True
    allow_web: bool = True
    allow_guest: bool = False
    concurrent_sessions: int = 4


class PackageCreate(BaseModel):
    name: str
    version: str
    category: str
    installer_type: str
    silent_supported: bool = False
    install_args: str = ""
    entry_path: str
    share_slug: str
    is_enabled: bool = True


class DeviceCreate(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str | None = None
    state: str = "online"
    profile: str = "guest"
    device_type: str = "client"
    agent_version: str | None = None
    notes: str = ""


class JobCreate(BaseModel):
    name: str
    job_type: str
    target_selector: str
    share_slug: str | None = None
    package_id: int | None = None
    queued: int = 0
    last_message: str = ""


class OverviewResponse(BaseModel):
    project_name: str
    status: str
    auth_mode: str
    shares: list[ShareSummary]
    devices: list[DeviceSummary]
    jobs: list[JobSummary]
    policies: list[PolicySummary]
    packages: list[PackageSummary]
