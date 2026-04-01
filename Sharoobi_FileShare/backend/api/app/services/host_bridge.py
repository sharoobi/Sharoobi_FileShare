from datetime import UTC, datetime
import re

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Device, Share
from app.schemas.bridge import HostBridgeBootstrapResponse, HostBridgeSharePlan, HostBridgeTelemetryRequest


def default_smb_share_name(slug: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", slug).strip("_")
    candidate = f"Sharoobi_{cleaned}" if cleaned else "Sharoobi_Share"
    return candidate[:80]


def build_bootstrap_response(session: Session, node_name: str) -> HostBridgeBootstrapResponse:
    shares = session.execute(
        select(Share).options(joinedload(Share.policy)).where(Share.is_enabled.is_(True)).order_by(Share.name.asc())
    ).scalars().all()
    items = [
        HostBridgeSharePlan(
            id=share.id,
            slug=share.slug,
            name=share.name,
            source_path=share.source_path,
            smb_share_name=share.smb_share_name or default_smb_share_name(share.slug),
            expose_via_smb=share.expose_via_smb,
            expose_via_web=share.expose_via_web,
            allow_guest=share.allow_guest,
            access_mode=share.access_mode,
            publish_strategy=share.publish_strategy,
            read_limit_mbps=share.policy.read_limit_mbps if share.policy else 0,
            is_enabled=share.is_enabled,
            notes=share.notes,
        )
        for share in shares
    ]
    return HostBridgeBootstrapResponse(
        node_name=node_name,
        generated_at=datetime.now(tz=UTC),
        shares=items,
    )


def apply_bridge_telemetry(session: Session, payload: HostBridgeTelemetryRequest) -> int:
    updated = 0
    now = datetime.now(tz=UTC)

    device = session.scalar(select(Device).where(Device.hostname == payload.node_name))
    if device is None:
        device = Device(
            hostname=payload.node_name,
            profile="infrastructure",
            state="online",
            device_type="host-bridge",
        )
        session.add(device)

    device.ip_address = payload.ip_address
    device.agent_version = payload.agent_version
    device.last_seen_at = now
    device.notes = "Windows Host Bridge"

    shares = {
        share.slug: share
        for share in session.execute(select(Share)).scalars().all()
    }
    for item in payload.shares:
        share = shares.get(item.slug)
        if share is None:
            continue
        share.source_path = item.source_path
        if item.smb_share_name:
            share.smb_share_name = item.smb_share_name
        share.last_bridge_status = item.access_state
        share.last_bridge_message = item.message
        share.last_bridge_node = payload.node_name
        share.last_path_exists = item.path_exists
        share.last_path_kind = item.path_kind
        share.last_smb_published = item.smb_published
        share.last_smb_publish_at = now if item.smb_published else share.last_smb_publish_at
        share.last_scanned_at = now
        share.file_count = item.file_count
        share.size_bytes = item.size_bytes
        updated += 1

    session.commit()
    return updated
