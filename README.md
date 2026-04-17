# TravelBuddy Agent API

AI travel assistant for Vietnam, deployed as a production-ready REST API with rate limiting, cost guard, and conversation history.

## Architecture

```
Client → Nginx (LB) → Agent x3 → Redis
```

- **Nginx** — round-robin load balancer
- **Agent** — FastAPI + LangGraph (GPT-4o-mini)
- **Redis** — conversation history, rate limiting, cost tracking

## Features

- REST API with conversation history
- API key authentication
- Rate limiting: 10 req/min per user
- Cost guard: $10/month per user
- Health & readiness endpoints
- Graceful shutdown
- Structured JSON logging

## Local Development

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### Setup

```bash
# 1. Clone and enter project
git clone <repo-url>
cd day12-agent-deployment

# 2. Set environment variables
export OPENAI_API_KEY=sk-proj-...
export AGENT_API_KEY=your-secret-key

# 3. Start services (3 agent replicas + Redis + Nginx)
docker compose up --build --scale agent=3

# 4. Test
curl http://localhost/health
```

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `AGENT_API_KEY` | Yes | — | Secret key for clients to call this API |
| `REDIS_URL` | No | `redis://redis:6379` | Redis connection URL |
| `PORT` | No | `8000` | Server port |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `RATE_LIMIT_PER_MINUTE` | No | `10` | Max requests per minute per user |
| `MONTHLY_BUDGET_USD` | No | `10.0` | Max OpenAI spend per user per month |

## API Reference

### `GET /health`
Liveness check. Returns `200` if the server is running.

```bash
curl https://your-domain/health
# {"status":"ok","timestamp":"2026-04-17T10:00:00+00:00"}
```

### `GET /ready`
Readiness check. Returns `200` if Redis is reachable, `503` otherwise.

```bash
curl https://your-domain/ready
# {"status":"ready","redis":"ok"}
```

### `POST /ask`
Send a question to the travel agent.

**Headers:**
- `X-Api-Key: <AGENT_API_KEY>` (required)
- `Content-Type: application/json`

**Body:**
```json
{
  "question": "Bay từ Hà Nội đến Đà Nẵng?",
  "conversation_id": "session-1"
}
```

- `conversation_id` is optional (default: `"default"`). Use the same value across requests to maintain conversation context.

**Response:**
```json
{
  "answer": "...",
  "conversation_id": "session-1",
  "cost_usd": 0.000012
}
```

**Error codes:**
| Code | Reason |
|---|---|
| `401` | Invalid or missing `X-Api-Key` |
| `402` | Monthly budget exceeded |
| `429` | Rate limit exceeded (10 req/min) |
| `503` | Redis unavailable |

### Example — Multi-turn conversation

```bash
# Turn 1
curl -X POST https://your-domain/ask \
  -H "X-Api-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Bay từ Hà Nội đến Đà Nẵng?", "conversation_id": "s1"}'

# Turn 2 — agent remembers context from turn 1
curl -X POST https://your-domain/ask \
  -H "X-Api-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Còn khách sạn ở đó thì sao?", "conversation_id": "s1"}'
```

## Deploy to Railway

### Prerequisites
- [Railway CLI](https://docs.railway.app/develop/cli): `npm install -g @railway/cli`
- [Upstash](https://upstash.com) account (free Redis)

### Steps

```bash
# 1. Login
railway login

# 2. Initialize project
railway init

# 3. Set environment variables
railway variables set \
  OPENAI_API_KEY=sk-proj-... \
  AGENT_API_KEY=your-secret-key \
  REDIS_URL=rediss://default:PASSWORD@HOST.upstash.io:6379

# 4. Deploy
railway up --detach

# 5. Get public URL
# Railway dashboard → service → Settings → Networking → Generate Domain
```

### View logs

```bash
railway logs --tail
```
