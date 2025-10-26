from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ==============================
# Request DTO
# ==============================


class SignupRequest(BaseModel):
    """サインアップ用リクエスト"""

    email: EmailStr
    first_name: str
    last_name: str
    password: str


class LoginRequest(BaseModel):
    """ログイン用リクエスト"""

    email: EmailStr
    password: str


# ==============================
# Response DTO（共通単位）
# ==============================


class AccountResponse(BaseModel):
    """共通アカウントレスポンス"""

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
    """サインアップ後のレスポンス"""

    account: AccountResponse


class LoginResponse(BaseModel):
    """ログイン成功レスポンス"""

    account: AccountResponse
    access_token: str


class RefreshResponse(BaseModel):
    """トークンリフレッシュ時のレスポンス"""

    account: AccountResponse
    access_token: str


class MeResponse(BaseModel):
    """ログインユーザー情報取得レスポンス"""

    account: AccountResponse


class LogoutResponse(BaseModel):
    """ログアウト時のレスポンス"""

    message: str = Field(default="Logged out successfully")
