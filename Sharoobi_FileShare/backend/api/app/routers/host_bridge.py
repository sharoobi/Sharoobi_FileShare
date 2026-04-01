from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.deps import AuthContext, require_permissions
from app.schemas.bridge import HostBridgeBootstrapResponse, HostBridgeTelemetryRequest, HostBridgeTelemetryResponse
from app.services.host_bridge import apply_bridge_telemetry, build_bootstrap_response

router = APIRouter(prefix="/api/host-bridge", tags=["host-bridge"])


@router.get("/bootstrap", response_model=HostBridgeBootstrapResponse)
def get_bootstrap_plan(
    _: AuthContext = Depends(require_permissions("shares:read")),
    session: Session = Depends(get_session),
) -> HostBridgeBootstrapResponse:
    settings = get_settings()
    return build_bootstrap_response(session, settings.host_node_name)


@router.post("/telemetry", response_model=HostBridgeTelemetryResponse)
def submit_telemetry(
    payload: HostBridgeTelemetryRequest,
    _: AuthContext = Depends(require_permissions("shares:write", "devices:write")),
    session: Session = Depends(get_session),
) -> HostBridgeTelemetryResponse:
    updated = apply_bridge_telemetry(session, payload)
    return HostBridgeTelemetryResponse(updated=updated, node_name=payload.node_name)
