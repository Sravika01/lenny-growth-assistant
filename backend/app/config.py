from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Find the project root folder
BASE_DIR = Path(__file__).resolve().parents[2]

# The .env file is in the project root
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    database_url: str

    default_llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()