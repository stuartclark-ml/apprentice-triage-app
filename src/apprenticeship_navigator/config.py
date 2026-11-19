import os
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

    database_url: SecretStr | None = None
    # Read by docker compose for the local database; declared so Settings accepts it.
    postgres_password: SecretStr | None = None


settings = Settings()

# LangSmith reads its settings from the process environment, not from Settings.
# Export only these three, and only when tracing is on and a key is present.
if settings.langsmith_tracing and settings.langsmith_api_key is not None:
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault(
        "LANGSMITH_API_KEY", settings.langsmith_api_key.get_secret_value()
    )
    os.environ.setdefault("LANGSMITH_PROJECT", settings.langsmith_project)
