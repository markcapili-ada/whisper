from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    username: str
    password: str
    url: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AUDIO_FILE_SERVER_",
        extra="ignore",
    )


settings = Settings()
