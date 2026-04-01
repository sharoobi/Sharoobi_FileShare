from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.deps import AuthContext, require_permissions
from app.models import Device
from app.schemas.domain import DeviceCreate, DeviceSummary
from app.services.queries import list_devices

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("", response_model=list[DeviceSummary])
def get_devices(
    _: AuthContext = Depends(require_permissions("devices:read")),
    session: Session = Depends(get_session),
) -> list[DeviceSummary]:
    return list_devices(session)


@router.post("", response_model=DeviceSummary)
def register_or_update_device(
    payload: DeviceCreate,
    _: AuthContext = Depends(require_permissions("devices:write")),
    session: Session = Depends(get_session),
) -> DeviceSummary:
    device = session.scalar(select(Device).where(Device.hostname == payload.hostname))
    if device is None:
        device = Device(hostname=payload.hostname)
        session.add(device)

    device.ip_address = payload.ip_address
    device.mac_address = payload.mac_address
    device.state = payload.state
    device.profile = payload.profile
    device.device_type = payload.device_type
    device.agent_version = payload.agent_version
    device.notes = payload.notes
    device.last_seen_at = datetime.now(tz=UTC)

    session.commit()
    refreshed = next(item for item in list_devices(session) if item.hostname == payload.hostname)
    return refreshed
