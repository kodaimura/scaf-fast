from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ._repository import AccountRepository
from .model import Account


class AccountModule:
    def __init__(self, db: Session):
        self.repo = AccountRepository(db)

    def create(self, entity: Account) -> Account:
        return self.repo.create(entity)

    def get_all(self) -> list[Account]:
        return self.repo.get()

    def get_by_id(self, account_id: int) -> Optional[Account]:
        entity = Account(id=account_id)
        return self.repo.get_one(entity)

    def get_by_email(self, email: str) -> Optional[Account]:
        entity = Account(email=email)
        return self.repo.get_one(entity)

    def get_by_login_id(self, login_id: str) -> Optional[Account]:
        entity = Account(login_id=login_id)
        return self.repo.get_one(entity)

    def update(self, entity: Account) -> Account:
        return self.repo.update(entity)

    def disable(self, entity: Account) -> Account:
        entity.disabled_at = datetime.now(timezone.utc)
        entity.token_version += 1
        return self.repo.update(entity)

    def enable(self, entity: Account) -> Account:
        entity.disabled_at = None
        return self.repo.update(entity)

    def delete(self, entity: Account, soft: bool = True) -> bool:
        return self.repo.delete(entity, soft=soft)


__all__ = ["AccountModule", "Account"]
