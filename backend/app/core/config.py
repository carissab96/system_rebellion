# backend/app/core/config.py
from __future__ import annotations

from functools import lru_cache
from typing import List, Any
from pathlib import Path
import json

from pydantic import Field, field_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str | None:
    """Walk upward from this file until we find a .env. Stop after 8 levels."""
    here = Path(__file__).resolve()
    for parent in [here.parent] + list(here.parents):
        candidate = parent / ".env"
        if candidate.exists():
            return str(candidate)
        # look for common names too
        for name in (".env.development", ".env.dev", ".env.local", ".env.production"):
            c2 = parent / name
            if c2.exists():
                return str(c2)
    return None


class Settings(BaseSettings):
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours for development
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:8000", "ws://localhost:5173", "ws://localhost:8000"]

    # App
    ENV: str = Field(
        default="dev",
        validation_alias=AliasChoices("ENV", "ENVIRONMENT"),
    )
    DEBUG: bool = False

    # Database (accept both names)
    DB_URL: str = Field(
        default="postgresql+asyncpg://carissab@localhost:5432/system_rebellion",
        validation_alias=AliasChoices("DB_URL", "DATABASE_URL"),
    )

    # Misc
    RENDER_API_KEY: str | None = None
    REDIS_URL: str | None = None

    # Pydantic v2 config: load .env no matter where uvicorn is run from
    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def _require_secret(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("SECRET_KEY is required and cannot be empty")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors(cls, v: Any) -> List[str]:
        # Accept JSON array or comma-separated string
        if isinstance(v, list):
            return [s.strip() for s in v]
        if isinstance(v, str):
            s = v.strip()
            # Try JSON first
            if s.startswith("["):
                try:
                    data = json.loads(s)
                    if isinstance(data, list):
                        return [str(x).strip() for x in data]
                except Exception:
                    pass
            # Fallback: comma-separated
            return [part.strip() for part in s.split(",") if part.strip()]
        return ["http://localhost:5173", "http://localhost:8000"]


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    print(f"[config] Loaded settings: ENV={s.ENV} DEBUG={s.DEBUG} ENV_FILE={Settings.model_config.get('env_file')}")
    return s


# Legacy module-level export
settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
