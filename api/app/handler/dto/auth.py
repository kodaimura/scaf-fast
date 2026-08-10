from datetime import datetime
from pydantic import BaseModel, EmailStr


# ==============================
# Request DTO
# ==============================


class SignupRequest(BaseModel):
    login_id: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class LoginRequest(BaseModel):
    login_id: str
    password: str
    remember_me: bool = False


# ==============================
# Response DTO
# ==============================


class AccountResponse(BaseModel):
    id: int
    email: EmailStr | None = None
    login_id: str
    first_name: str
    last_name: str
    disabled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SignupResponse(BaseModel):
    account: AccountResponse


class LoginResponse(BaseModel):
    account: AccountResponse
    access_token: str


class RefreshResponse(BaseModel):
    access_token: str


class LogoutResponse(BaseModel):
    pass
