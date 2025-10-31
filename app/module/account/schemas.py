from pydantic import BaseModel, EmailStr
from datetime import datetime


class AccountDto(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountCreateDto(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
