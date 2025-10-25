from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from passlib.context import CryptContext

from domain.accounts.models import Account
from domain.accounts.schemas import AccountCreate, AccountUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AccountRepository:
    """アカウント関連のDB操作を担うリポジトリ層"""

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # Create
    # -----------------------------
    def create(self, data: AccountCreate) -> Account:
        hashed_password = pwd_context.hash(data.password)
        account = Account(
            email=data.email,
            password_hash=hashed_password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    # -----------------------------
    # Read
    # -----------------------------
    def get_by_id(self, account_id: int) -> Optional[Account]:
        stmt = select(Account).where(
            Account.id == account_id, Account.deleted_at.is_(None)
        )
        return self.db.scalars(stmt).first()

    def get_by_email(self, email: str) -> Optional[Account]:
        stmt = select(Account).where(
            Account.email == email, Account.deleted_at.is_(None)
        )
        return self.db.scalars(stmt).first()

    def list(self) -> List[Account]:
        stmt = select(Account).where(Account.deleted_at.is_(None))
        return self.db.scalars(stmt).all()

    # -----------------------------
    # Update
    # -----------------------------
    def update(self, account_id: int, data: AccountUpdate) -> Optional[Account]:
        account = self.get_by_id(account_id)
        if not account:
            return None

        if data.first_name is not None:
            account.first_name = data.first_name
        if data.last_name is not None:
            account.last_name = data.last_name
        if data.password is not None:
            account.password_hash = pwd_context.hash(data.password)

        self.db.commit()
        self.db.refresh(account)
        return account

    # -----------------------------
    # Delete (論理削除)
    # -----------------------------
    def soft_delete(self, account_id: int) -> bool:
        account = self.get_by_id(account_id)
        if not account:
            return False

        account.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
