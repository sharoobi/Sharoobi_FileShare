from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import decode_access_token
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user_id: int | None
    username: str
    full_name: str
    is_superuser: bool
    roles: list[str]
    permissions: set[str]


def get_current_actor(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> AuthContext:
    settings = get_settings()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    token = credentials.credentials
    if token == settings.bootstrap_api_token:
        return AuthContext(
            user_id=None,
            username="bootstrap-token",
            full_name="Bootstrap API Token",
            is_superuser=True,
            roles=["admin"],
            permissions={"*"},
        )

    try:
        payload = decode_access_token(token, settings)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
        ) from exc

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token subject.",
        )

    user = session.scalar(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == int(subject))
    )
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or missing.",
        )

    permissions = set()
    role_slugs: list[str] = []
    for role in user.roles:
        role_slugs.append(role.slug)
        permissions.update(role.permissions)

    return AuthContext(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        is_superuser=user.is_superuser,
        roles=role_slugs,
        permissions=permissions,
    )


def require_permissions(*required: str):
    def dependency(actor: AuthContext = Depends(get_current_actor)) -> AuthContext:
        if actor.is_superuser or "*" in actor.permissions:
            return actor
        missing = [permission for permission in required if permission not in actor.permissions]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing)}",
            )
        return actor

    return dependency
