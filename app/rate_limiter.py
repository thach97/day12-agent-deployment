import time
import uuid

from fastapi import Depends, HTTPException

from auth import verify_api_key
from config import settings
from redis_client import redis as _redis


def check_rate_limit(user_id: str = Depends(verify_api_key)) -> None:
    key = f"rate:{user_id}"
    now = time.time()
    window_start = now - 60

    with _redis.pipeline() as pipe:
        pipe.zremrangebyscore(key, "-inf", window_start)
        pipe.zcard(key)
        _, count = pipe.execute()

    if count >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.RATE_LIMIT_PER_MINUTE} req/min",
        )

    # Record this request after the check to avoid counting blocked requests
    _redis.zadd(key, {f"{now}-{uuid.uuid4()}": now})
    _redis.expire(key, 61)
