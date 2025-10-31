from typing import Optional
from sqlalchemy.orm import Session
from .repository import AccountRepository
from .model import Account


class AccountModule:
    def __init__(self, db: Session):
        self.repo = AccountRepository(db)

    def create(self, entity: Account) -> Account:
        return self.repo.create(entity)

    def get_by_id(self, account_id: int) -> Optional[Account]:
        entity = Account(id=account_id)
        return self.repo.get_one(entity)

    def get_by_email(self, email: str) -> Optional[Account]:
        entity = Account(email=email)
        return self.repo.get_one(entity)

    def update(self, entity: Account) -> Account:
        return self.repo.update(entity)

    def delete(self, entity: Account, soft: bool = True) -> bool:
        return self.repo.delete(entity, soft=soft)


__all__ = ["Account", "AccountModule"]
