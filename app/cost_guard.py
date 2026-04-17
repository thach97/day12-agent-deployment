from datetime import datetime

from fastapi import Depends, HTTPException

from auth import verify_api_key
from config import settings
from redis_client import redis as _redis


def _cost_key(user_id: str) -> str:
    month = datetime.now().strftime("%Y-%m")
    return f"cost:{user_id}:{month}"


def check_budget(user_id: str = Depends(verify_api_key)) -> None:
    spent = float(_redis.get(_cost_key(user_id)) or 0)
    if spent >= settings.MONTHLY_BUDGET_USD:
        raise HTTPException(
            status_code=402,
            detail=f"Monthly budget of ${settings.MONTHLY_BUDGET_USD:.2f} exceeded (spent ${spent:.4f})",
        )


def add_cost(user_id: str, cost_usd: float) -> None:
    key = _cost_key(user_id)
    _redis.incrbyfloat(key, cost_usd)
    _redis.expire(key, 35 * 24 * 3600)  # keep for 35 days to cover month boundary
