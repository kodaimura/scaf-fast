from app.module.blacklist.repository import BlacklistRepository
from app.module.blacklist.schemas import BlacklistAddDto
from app.core.config import config


class BlacklistService:
    def __init__(self):
        self.enabled = config.USE_BLACKLIST
        self.repo = BlacklistRepository() if self.enabled else None

    def add(self, dto: BlacklistAddDto):
        if not self.enabled:
            return
        exp_ts = int(dto.expires_at.timestamp())
        self.repo.add(dto.jti, exp_ts)

    def is_revoked(self, jti: str) -> bool:
        if not self.enabled:
            return False
        return self.repo.exists(jti)
