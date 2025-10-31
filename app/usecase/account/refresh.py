from dataclasses import dataclass
from fastapi import HTTPException
from app.module.blacklist.module import BlacklistModule
from app.core.jwt import create_access_token


@dataclass(frozen=True)
class RefreshInput:
    jti: str
    sub: str


@dataclass(frozen=True)
class RefreshResult:
    access_token: str


class RefreshUsecase:
    def __init__(self):
        pass

    def execute(self, input: RefreshInput) -> RefreshResult:
        if not input.jti or not input.sub:
            raise HTTPException(status_code=400, detail="Malformed token")

        module = BlacklistModule()
        if module.is_revoked(input.jti):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        access_token = create_access_token({"sub": input.sub})
        return RefreshResult(access_token=access_token)
