from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.crypto import hash_password, verify_password
from .repository import AccountRepository
from .schemas import AccountCreateDto, AccountDto
from .model import Account


class AccountService:
    def __init__(self, db: Session):
        self.repo = AccountRepository(db)

    def create(self, dto: AccountCreateDto) -> AccountDto:
        existing = self.repo.get_by_email(dto.email)
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            )

        account = self.repo.create(
            Account(
                email=dto.email,
                password_hash=hash_password(dto.password),
                first_name=dto.first_name,
                last_name=dto.last_name,
            )
        )
        return AccountDto.from_orm(account)

    def get_by_id(self, account_id: int) -> AccountDto:
        account = self.repo.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found",
            )
        return AccountDto.from_orm(account)

    def authenticate(self, email: str, password: str):
        account = self.repo.get_by_email(email)
        if not account or not verify_password(password, account.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return account
