from datetime import datetime
from app.module.blacklist.repository import BlacklistRepository
from app.module.blacklist.schemas import BlacklistAddDto


class BlacklistService:
    def __init__(self):
        self.repo = BlacklistRepository()

    def add(self, dto: BlacklistAddDto):
        exp_ts = int(dto.expires_at.timestamp())
        self.repo.add(dto.jti, exp_ts)

    def is_revoked(self, jti: str) -> bool:
        return self.repo.exists(jti)
