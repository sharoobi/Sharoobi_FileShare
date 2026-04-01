from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.deps import AuthContext, require_permissions
from app.models import AccessPolicy
from app.schemas.domain import PolicyCreate, PolicySummary
from app.services.queries import list_policies

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.get("", response_model=list[PolicySummary])
def get_policies(
    _: AuthContext = Depends(require_permissions("policies:read")),
    session: Session = Depends(get_session),
) -> list[PolicySummary]:
    return list_policies(session)


@router.post("", response_model=PolicySummary, status_code=status.HTTP_201_CREATED)
def create_policy(
    payload: PolicyCreate,
    _: AuthContext = Depends(require_permissions("policies:write")),
    session: Session = Depends(get_session),
) -> PolicySummary:
    existing = session.scalar(select(AccessPolicy).where(AccessPolicy.slug == payload.slug))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Policy slug already exists.")

    policy = AccessPolicy(**payload.model_dump())
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return PolicySummary.model_validate(policy)
