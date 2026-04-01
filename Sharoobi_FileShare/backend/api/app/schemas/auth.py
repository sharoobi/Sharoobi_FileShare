from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthProfile(BaseModel):
    user_id: int | None
    username: str
    full_name: str
    is_superuser: bool
    roles: list[str]
    permissions: list[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthProfile
