from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from .model import Account


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity: Account) -> Account:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_by_email(self, email: str) -> Optional[Account]:
        stmt = select(Account).where(
            Account.email == email,
            Account.deleted_at.is_(None),
        )
        return self.db.scalars(stmt).first()

    def get_by_id(self, account_id: int) -> Optional[Account]:
        stmt = select(Account).where(
            Account.id == account_id,
            Account.deleted_at.is_(None),
        )
        return self.db.scalars(stmt).first()

    def soft_delete(self, account_id: int) -> bool:
        account = self.get_by_id(account_id)
        if not account:
            return False
        account.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
