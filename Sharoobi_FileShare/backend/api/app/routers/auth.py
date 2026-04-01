from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import create_access_token, verify_password
from app.deps import AuthContext, get_current_actor
from app.schemas.auth import AuthProfile, LoginRequest, TokenResponse
from app.services.queries import get_user_with_roles

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    settings = get_settings()
    user = get_user_with_roles(session, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    permissions = sorted({permission for role in user.roles for permission in role.permissions})
    roles = [role.slug for role in user.roles]
    token, expires_in = create_access_token(
        settings=settings,
        subject=str(user.id),
        username=user.username,
        roles=roles,
        permissions=permissions,
    )
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=AuthProfile(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            is_superuser=user.is_superuser,
            roles=roles,
            permissions=permissions,
        ),
    )


@router.get("/me", response_model=AuthProfile)
def me(actor: AuthContext = Depends(get_current_actor)) -> AuthProfile:
    return AuthProfile(
        user_id=actor.user_id,
        username=actor.username,
        full_name=actor.full_name,
        is_superuser=actor.is_superuser,
        roles=actor.roles,
        permissions=sorted(actor.permissions),
    )
