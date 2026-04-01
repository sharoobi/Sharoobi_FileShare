from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.deps import AuthContext, require_permissions
from app.models import AccessPolicy, Share
from app.schemas.domain import ShareCreate, ShareSummary, ShareUpdate
from app.services.host_bridge import default_smb_share_name
from app.services.queries import list_shares, share_to_summary

router = APIRouter(prefix="/api/shares", tags=["shares"])


@router.get("", response_model=list[ShareSummary])
def get_shares(
    _: AuthContext = Depends(require_permissions("shares:read")),
    session: Session = Depends(get_session),
) -> list[ShareSummary]:
    return list_shares(session)


@router.post("", response_model=ShareSummary, status_code=status.HTTP_201_CREATED)
def create_share(
    payload: ShareCreate,
    _: AuthContext = Depends(require_permissions("shares:write")),
    session: Session = Depends(get_session),
) -> ShareSummary:
    existing = session.scalar(select(Share).where(Share.slug == payload.slug))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Share slug already exists.")

    policy = None
    if payload.policy_slug:
        policy = session.scalar(select(AccessPolicy).where(AccessPolicy.slug == payload.policy_slug))
        if policy is None:
            raise HTTPException(status_code=404, detail="Policy not found.")

    share = Share(
        slug=payload.slug,
        name=payload.name,
        source_path=payload.source_path,
        access_mode=payload.access_mode,
        publish_strategy=payload.publish_strategy,
        smb_share_name=payload.smb_share_name or default_smb_share_name(payload.slug),
        allow_guest=payload.allow_guest,
        expose_via_smb=payload.expose_via_smb,
        expose_via_web=payload.expose_via_web,
        is_enabled=payload.is_enabled,
        policy_id=policy.id if policy else None,
        notes=payload.notes,
    )
    session.add(share)
    session.commit()
    session.refresh(share)
    return share_to_summary(share)


@router.patch("/{share_id}", response_model=ShareSummary)
def update_share(
    share_id: int,
    payload: ShareUpdate,
    _: AuthContext = Depends(require_permissions("shares:write")),
    session: Session = Depends(get_session),
) -> ShareSummary:
    share = session.get(Share, share_id)
    if share is None:
        raise HTTPException(status_code=404, detail="Share not found.")

    data = payload.model_dump(exclude_unset=True)
    policy_slug = data.pop("policy_slug", None)
    if payload.policy_slug is not None:
        policy = session.scalar(select(AccessPolicy).where(AccessPolicy.slug == policy_slug))
        if policy is None:
            raise HTTPException(status_code=404, detail="Policy not found.")
        share.policy_id = policy.id
    if "smb_share_name" in data and not data["smb_share_name"]:
        data["smb_share_name"] = default_smb_share_name(share.slug)

    for key, value in data.items():
        setattr(share, key, value)

    session.commit()
    session.refresh(share)
    return share_to_summary(share)
