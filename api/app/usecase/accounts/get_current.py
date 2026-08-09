from dataclasses import dataclass
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.module.account.module import AccountModule, Account


@dataclass(frozen=True)
class GetCurrentAccountInput:
    account_id: int


class GetCurrentAccountUsecase:
    def __init__(self, db: Session):
        self.module = AccountModule(db)

    def execute(self, input: GetCurrentAccountInput) -> Account:
        account = self.module.get_by_id(input.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
