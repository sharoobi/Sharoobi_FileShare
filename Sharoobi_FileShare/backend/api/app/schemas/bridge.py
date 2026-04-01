from datetime import datetime

from pydantic import BaseModel


class HostBridgeSharePlan(BaseModel):
    id: int
    slug: str
    name: str
    source_path: str
    smb_share_name: str
    expose_via_smb: bool
    expose_via_web: bool
    allow_guest: bool
    access_mode: str
    publish_strategy: str
    read_limit_mbps: int
    is_enabled: bool
    notes: str


class HostBridgeBootstrapResponse(BaseModel):
    node_name: str
    generated_at: datetime
    shares: list[HostBridgeSharePlan]


class ShareTelemetryPayload(BaseModel):
    slug: str
    source_path: str
    path_exists: bool
    path_kind: str
    file_count: int | None = None
    size_bytes: int | None = None
    access_state: str
    message: str = ""
    smb_share_name: str | None = None
    smb_published: bool = False


class HostBridgeTelemetryRequest(BaseModel):
    node_name: str
    agent_version: str = "host-bridge-0.1.0"
    ip_address: str = ""
    shares: list[ShareTelemetryPayload]


class HostBridgeTelemetryResponse(BaseModel):
    updated: int
    node_name: str
