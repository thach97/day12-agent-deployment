import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from pythonjsonlogger import jsonlogger
from pydantic import BaseModel

from agent import run_agent
from auth import verify_api_key
from config import settings
from cost_guard import add_cost, check_budget
from rate_limiter import check_rate_limit

# ── Structured JSON logging ───────────────────────────────────────────────────
_handler = logging.StreamHandler()
_handler.setFormatter(
    jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s")
)
logging.root.handlers = [_handler]
logging.root.setLevel(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# ── Redis client (shared, stateless) ─────────────────────────────────────────
from redis_client import redis as _redis

HISTORY_TTL = 86400  # 24 h per conversation


# ── Lifespan (graceful shutdown) ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Agent service starting", extra={"port": settings.PORT})
    yield
    logger.info("Agent service shutting down gracefully")
    _redis.close()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="TravelBuddy Agent API", version="1.0.0", lifespan=lifespan)


# ── Schemas ───────────────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str
    conversation_id: str = "default"


class AskResponse(BaseModel):
    answer: str
    conversation_id: str
    cost_usd: float


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/ready")
def ready():
    try:
        _redis.ping()
        return {"status": "ready", "redis": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {exc}")


@app.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    user_id: str = Depends(verify_api_key),
    _rl: None = Depends(check_rate_limit),
    _bg: None = Depends(check_budget),
):
    history_key = f"history:{user_id}:{request.conversation_id}"

    # Load conversation history from Redis
    raw = _redis.get(history_key)
    stored: list[dict] = json.loads(raw) if raw else []

    # Build LangChain message list from stored history + new question
    messages = []
    for msg in stored:
        if msg["role"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=request.question))

    t0 = time.perf_counter()
    answer, usage = run_agent(messages)
    elapsed = time.perf_counter() - t0

    # Estimate cost — GPT-4o-mini: $0.15/1M input, $0.60/1M output
    input_tokens: int = usage.get("input_tokens", 0)
    output_tokens: int = usage.get("output_tokens", 0)
    cost_usd = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000

    # Persist updated history
    stored.append({"role": "human", "content": request.question})
    stored.append({"role": "assistant", "content": answer})
    _redis.setex(history_key, HISTORY_TTL, json.dumps(stored))

    # Accumulate spend for this user
    add_cost(user_id, cost_usd)

    logger.info(
        "Request processed",
        extra={
            "user_id": user_id,
            "conversation_id": request.conversation_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost_usd, 6),
            "elapsed_s": round(elapsed, 3),
        },
    )

    return AskResponse(
        answer=answer,
        conversation_id=request.conversation_id,
        cost_usd=round(cost_usd, 6),
    )
