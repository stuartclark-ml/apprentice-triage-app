from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    apprenticeship_api_key: str
    app_env: str = "development"
    log_level: str = "debug"


settings = Settings()
