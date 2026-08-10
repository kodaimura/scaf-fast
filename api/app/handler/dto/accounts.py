from datetime import datetime
from pydantic import BaseModel, EmailStr


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


class PostAccountRequest(BaseModel):
    login_id: str | None = None
    email: EmailStr | None = None
    first_name: str
    last_name: str
    password: str


class PutAccountRequest(BaseModel):
    login_id: str | None = None
    email: EmailStr | None = None
    first_name: str
    last_name: str
    password: str | None = None


class GetAccountsResponse(BaseModel):
    accounts: list[AccountResponse]


class GetCurrentAccountResponse(BaseModel):
    account: AccountResponse


class GetAccountResponse(BaseModel):
    account: AccountResponse


class PostAccountResponse(BaseModel):
    account: AccountResponse


class PutAccountResponse(BaseModel):
    account: AccountResponse


class PutAccountDisableResponse(BaseModel):
    account: AccountResponse


class PutAccountEnableResponse(BaseModel):
    account: AccountResponse
