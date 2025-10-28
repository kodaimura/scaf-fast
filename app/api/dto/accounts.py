from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ==============================
# Request DTO
# ==============================


class SignupRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==============================
# Response DTO（共通単位）
# ==============================


class AccountResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==============================
# Response DTO（API単位）
# ==============================


class SignupResponse(BaseModel):
    account: AccountResponse


class LoginResponse(BaseModel):
    account: AccountResponse
    access_token: str


class RefreshResponse(BaseModel):
    access_token: str


class MeResponse(BaseModel):
    account: AccountResponse


class LogoutResponse(BaseModel):
    pass
