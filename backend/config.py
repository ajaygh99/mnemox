# config.py — Mnemox Settings (Step 7: + Stripe + JWT)

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = Field(default="http://localhost:54321")
    supabase_anon_key: str = Field(default="dev-anon-key")
    supabase_service_key: str = Field(default="dev-service-key")
    supabase_jwt_secret: str = Field(default="super-secret-jwt-key-for-dev-only-32chars!")

    # OpenAI
    openai_api_key: str = Field(default="sk-placeholder")

    # Qdrant
    qdrant_url: str = Field(default=":memory:")
    qdrant_api_key: str = Field(default="")

    # Stripe
    stripe_secret_key: str = Field(default="sk_test_placeholder")
    stripe_webhook_secret: str = Field(default="whsec_placeholder")
    stripe_pro_price_id: str = Field(default="price_pro_placeholder")
    stripe_team_price_id: str = Field(default="price_team_placeholder")
    stripe_publishable_key: str = Field(default="pk_test_placeholder")

    # App
    api_secret_key: str = Field(default="dev-api-key-change-in-production")
    app_env: str = Field(default="development")
    app_port: int = Field(default=8000)
    cors_origins: str = Field(default="chrome-extension://*,http://localhost:3000,http://localhost:5173")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
