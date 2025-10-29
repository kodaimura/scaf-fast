import os
import redis
from app.core.config import config

def get_redis():
    return redis.Redis.from_url(config.REDIS_URL, decode_responses=True)
