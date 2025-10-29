from datetime import datetime
from sqlalchemy.orm import Session
from .repository import BlacklistJtiRepository
from .schemas import BlacklistJtiDto
from .model import BlacklistJti


class BlacklistJtiService:
    def __init__(self, db: Session):
        self.repo = BlacklistJtiRepository(db)

    def add(self, dto: BlacklistJtiDto) -> None:
        if self.repo.exists(dto.jti):
            return

        self.repo.create(
            BlacklistJti(
                jti=dto.jti,
                account_id=dto.account_id,
                expires_at=dto.expires_at,
            )
        )

    def exists(self, jti: str) -> bool:
        return self.repo.exists(jti)

    def cleanup_expired(self) -> int:
        return self.repo.delete_expired()
