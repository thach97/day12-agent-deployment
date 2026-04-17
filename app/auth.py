import hashlib

from fastapi import Header, HTTPException

from config import settings


def verify_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    # Derive a stable user_id from the key without exposing it in logs
    return hashlib.sha256(x_api_key.encode()).hexdigest()[:16]
