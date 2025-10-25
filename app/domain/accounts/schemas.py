from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# -----------------------------
# 基本スキーマ（共通部分）
# -----------------------------
class AccountBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    first_name: str = Field(..., example="Taro")
    last_name: str = Field(..., example="Yamada")


# -----------------------------
# 作成用スキーマ（入力）
# -----------------------------
class AccountCreate(AccountBase):
    password: str = Field(..., min_length=8, example="secret123")


# -----------------------------
# 更新用スキーマ（入力）
# -----------------------------
class AccountUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = Field(None, min_length=8)


# -----------------------------
# 出力用スキーマ（レスポンス）
# -----------------------------
class AccountRead(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        orm_mode = True
