from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/bittensor_intel"
    )
    REDIS_URL: str = "redis://localhost:6379/0"
    LLM_BASE_URL: str = "http://localhost:4000/v1"
    LLM_API_KEY: str = ""
    TAOSTATS_API_KEY: str = ""
    DISCORD_WEBHOOK_URL: str = ""
    POLL_INTERVAL_MINUTES: int = 15
    COLLECTION_INTERVAL_SECONDS: int = 900  # 15 minutes

    class Config:
        env_file = ".env"


settings = Settings()
