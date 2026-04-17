from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8000
    REDIS_URL: str = "redis://redis:6379"
    OPENAI_API_KEY: str = ""
    AGENT_API_KEY: str = "change-me-secret-key"
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_PER_MINUTE: int = 10
    MONTHLY_BUDGET_USD: float = 10.0



settings = Settings()
