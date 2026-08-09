from dataclasses import dataclass
from datetime import datetime, timezone
from app.core.error import AppError, ErrorCode
from app.module.blacklist.module import BlacklistModule, BlacklistAddDto


@dataclass(frozen=True)
class LogoutInput:
    jti: str
    exp: int


class LogoutUsecase:
    def __init__(self):
        pass

    def execute(self, input: LogoutInput) -> None:
        if not input.jti or not input.exp:
            raise AppError(code=ErrorCode.MALFORMED_TOKEN)

        module = BlacklistModule()
        module.add(
            BlacklistAddDto(
                jti=input.jti,
                expires_at=datetime.fromtimestamp(input.exp, tz=timezone.utc),
            )
        )
