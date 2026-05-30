# config.py — Mnemox Backend Configuration
# Loads all settings from environment variables / .env file

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # OpenAI (for embeddings — text-embedding-3-small)
    openai_api_key: str = ""

    # Qdrant vector DB
    qdrant_url: str = ""        # Leave empty to use in-memory (dev mode)
    qdrant_api_key: str = ""

    # Security
    api_secret_key: str = "dev-secret-change-in-production"

    # App
    app_env: str = "development"
    app_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
