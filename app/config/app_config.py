from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.celery_config import settings as celery_settings


class Settings(BaseSettings):
    env: str
    url: str
    port: int
    ai_env: str
    CELERY: ClassVar[dict] = celery_settings.model_dump()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
    )


settings = Settings()
