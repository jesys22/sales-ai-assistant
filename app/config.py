from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sales_ai"

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    qwen_base_url: str = "http://127.0.0.1:1234/v1"
    qwen_model: str = "qwen2.5-coder-14b-instruct"

    telegram_bot_token: str | None = None
    bitrix24_webhook_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()