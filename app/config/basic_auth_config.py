from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    username: str
    password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_BASIC_AUTH_",
        extra="ignore",
    )


settings = Settings()
