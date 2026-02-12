from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WEBHOOK_",
        extra="ignore",
    )


settings = Settings()
