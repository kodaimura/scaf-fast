from pydantic import BaseModel, EmailStr
from datetime import datetime


class AccountBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class AccountCreate(AccountBase):
    password: str


class AccountResponse(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    account: AccountResponse
    access_token: str
