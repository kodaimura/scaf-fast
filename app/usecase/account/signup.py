from dataclasses import dataclass
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.module.account.module import AccountModule, Account
from app.core.crypto import hash_password


@dataclass(frozen=True)
class SignupInput:
    email: str
    password: str
    first_name: str
    last_name: str


class SignupUsecase:
    def __init__(self, db: Session):
        self.db = db
        self.module = AccountModule(db)

    def execute(self, input: SignupInput) -> Account:
        existing = self.module.get_by_email(input.email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        hashed = hash_password(input.password)
        account = self.module.create(
            Account(
                email=input.email,
                password_hash=hashed,
                first_name=input.first_name,
                last_name=input.last_name,
            )
        )

        self.db.commit()
        return account
