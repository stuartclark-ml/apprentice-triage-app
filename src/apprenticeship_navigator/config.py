from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    apprenticeship_api_key: str
    app_env: str = "development"
    log_level: str = "debug"

    # Language model. Optional so tests and continuous integration run without a key.
    google_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.5-flash-lite"

    # LangSmith tracing. Declared here so Settings accepts these keys from .env;
    # the langsmith library itself reads them from the process environment.
    langsmith_tracing: bool = False
    langsmith_api_key: SecretStr | None = None
    langsmith_project: str = "apprenticeship-navigator-dev"


settings = Settings()
