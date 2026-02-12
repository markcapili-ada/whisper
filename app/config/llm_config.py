from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model: str
    api_url: str
    api_key: str
    client: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LLM_",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
