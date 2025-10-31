from datetime import datetime, timezone
from app.core.redis import get_redis
from app.core.config import config
from ._dto import BlacklistAddDto


class BlacklistModule:
    PREFIX = "blacklist:jti:"

    def __init__(self):
        self.enabled = config.USE_BLACKLIST
        self.redis = get_redis() if self.enabled else None

    def add(self, dto: BlacklistAddDto) -> None:
        if not self.enabled:
            return

        now_ts = int(datetime.now(tz=timezone.utc).timestamp())
        exp_ts = int(dto.expires_at.timestamp())
        ttl = max(0, exp_ts - now_ts)
        self.redis.setex(f"{self.PREFIX}{dto.jti}", ttl, "1")

    def is_revoked(self, jti: str) -> bool:
        if not self.enabled:
            return False
        return self.redis.exists(f"{self.PREFIX}{jti}") == 1

    def delete(self, jti: str) -> None:
        if not self.enabled:
            return
        self.redis.delete(f"{self.PREFIX}{jti}")


__all__ = ["BlacklistModule", "BlacklistAddDto"]
