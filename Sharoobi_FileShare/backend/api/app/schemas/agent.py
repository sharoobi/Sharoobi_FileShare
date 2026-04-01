from datetime import datetime

from pydantic import BaseModel


class AgentHeartbeatRequest(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str | None = None
    profile: str = "guest"
    agent_version: str = "windows-agent-0.1.0"
    notes: str = ""


class AgentHeartbeatResponse(BaseModel):
    hostname: str
    accepted: bool
    next_poll_seconds: int


class AgentJobManifest(BaseModel):
    job_id: int
    job_name: str
    job_type: str
    share_slug: str | None
    share_path: str | None
    package_name: str | None
    package_version: str | None
    entry_path: str | None
    installer_type: str | None
    install_args: str | None
    silent_supported: bool
    target_selector: str
    issued_at: datetime


class AgentJobStatusRequest(BaseModel):
    hostname: str
    state: str
    message: str = ""
    succeeded: int | None = None
    failed: int | None = None


class AgentJobStatusResponse(BaseModel):
    job_id: int
    state: str
    accepted: bool
