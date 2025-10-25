from sqlalchemy.orm import Session
from fastapi import HTTPException
from core.security import verify_password
from .repository import AccountRepository
from .schemas import AccountCreate


class AccountService:
    def __init__(self, db: Session):
        self.repo = AccountRepository(db)

    def create(self, data: AccountCreate):
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        return self.repo.create(data)

    def authenticate(self, email: str, password: str):
        account = self.repo.get_by_email(email)
        if not account or not verify_password(password, account.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return account

    def get_by_id(self, account_id: int):
        account = self.repo.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
