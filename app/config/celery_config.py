from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.redis_config import settings as redis_settings


class Settings(BaseSettings):
    broker_url: str = f"redis://{redis_settings.host}:{redis_settings.port}/0"
    result_backend: str = f"redis://{redis_settings.host}:{redis_settings.port}/0"
    task_ignore_result: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CELERY_",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
