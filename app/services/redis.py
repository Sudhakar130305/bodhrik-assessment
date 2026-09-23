import redis

from app.database import settings

redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)