from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from backend/.env when present."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NeuroSymbolic AI"
    environment: str = "development"
    database_url: str = "sqlite:///./data/neurosymbolic.db"
    neo4j_uri: str | None = None
    neo4j_user: str = "neo4j"
    neo4j_password: str | None = None
    hf_model_name: str = "facebook/bart-large-mnli"
    enable_transformers: bool = False
    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24
    cors_origins: list[str] | str = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

    @field_validator("cors_origins")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                import json
                try:
                    return json.loads(value)
                except Exception:
                    pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def neo4j_enabled(self) -> bool:
        return bool(self.neo4j_uri and self.neo4j_password)

    def validate_production_secrets(self) -> None:
        unsafe_defaults = {"development-only-change-me", "replace-with-a-long-random-secret"}
        if self.environment.lower() == "production" and self.jwt_secret in unsafe_defaults:
            raise RuntimeError("Set JWT_SECRET to a strong value before running in production.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production_secrets()
    # Ensure the database parent directory exists (works for any path)
    from urllib.parse import urlparse as _urlparse
    db_path = _urlparse(settings.database_url).path.lstrip("/")
    if db_path:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return settings
