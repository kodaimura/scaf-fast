from pydantic import BaseModel, EmailStr
from datetime import datetime


class AccountBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class AccountCreate(AccountBase):
    password: str


class AccountInternal(AccountBase):
    """DBから取得した内部用DTO"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
