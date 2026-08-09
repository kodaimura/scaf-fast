from datetime import datetime
from pydantic import BaseModel, EmailStr


class AccountResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GetCurrentAccountResponse(BaseModel):
    account: AccountResponse
