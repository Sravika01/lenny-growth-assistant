from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    database_url: str

    default_llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Render provides DATABASE_URL as postgresql://...
# SQLAlchemy async requires the asyncpg driver.
if settings.database_url.startswith("postgresql://"):
    settings.database_url = settings.database_url.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )