from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    url: str
    username: str
    password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AUTOCOLLECT_",
        extra="ignore",
    )


settings = Settings()
