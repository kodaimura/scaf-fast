from datetime import datetime, timezone
from app.core.redis import get_redis


class BlacklistRepository:
    PREFIX = "blacklist:jti:"

    def __init__(self):
        self.redis = get_redis()

    def add(self, jti: str, exp: int):
        now_ts = int(datetime.now(tz=timezone.utc).timestamp())
        ttl = max(0, exp - now_ts)
        self.redis.setex(f"{self.PREFIX}{jti}", ttl, "1")

    def exists(self, jti: str) -> bool:
        return self.redis.exists(f"{self.PREFIX}{jti}") == 1

    def delete(self, jti: str):
        self.redis.delete(f"{self.PREFIX}{jti}")
