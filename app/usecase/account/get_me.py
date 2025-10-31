from dataclasses import dataclass
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.module.account.module import AccountModule
from app.module.account.model import Account


@dataclass(frozen=True)
class GetMeInput:
    account_id: int


class GetMeUsecase:
    def __init__(self, db: Session):
        self.module = AccountModule(db)

    def execute(self, input: GetMeInput) -> Account:
        account = self.module.get_by_id(input.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
