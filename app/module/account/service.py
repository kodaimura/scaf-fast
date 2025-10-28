from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .repository import AccountRepository
from .schemas import AccountCreateDto, AccountDto
from .model import Account


class AccountService:
    def __init__(self, db: Session):
        self.repo = AccountRepository(db)

    def create(self, data: AccountCreateDto) -> AccountDto:
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        account = self.repo.create(Account(
            email=data.email,
            password_hash=data.password_hash,
            first_name=data.first_name,
            last_name=data.last_name,
        ))
        return AccountDto.from_orm(account)

    def get_by_id(self, account_id: int) -> AccountDto:
        account = self.repo.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return AccountDto.from_orm(account)

    def get_by_email(self, email: str) -> AccountDto | None:
        account = self.repo.get_by_email(email)
        return AccountDto.from_orm(account) if account else None
