from dataclasses import dataclass
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.modules.account.model import Account
from app.modules.account.module import AccountModule
from app.core.crypto import verify_password
from app.core.jwt import create_token_pair


@dataclass(frozen=True)
class LoginInput:
    email: str
    password: str


@dataclass(frozen=True)
class LoginResult:
    account: Account
    access_token: str
    refresh_token: str


class LoginUsecase:
    def __init__(self, db: Session):
        self.module = AccountModule(db)

    def execute(self, input: LoginInput) -> LoginResult:
        account = self.module.get_by_email(input.email)

        if not account or not verify_password(input.password, account.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token, refresh_token = create_token_pair(account.id)

        return LoginResult(
            account=account,
            access_token=access_token,
            refresh_token=refresh_token,
        )
