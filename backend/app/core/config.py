# app/core/config.py
from __future__ import annotations

import os
from typing import List, Union

from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,   # env var keys are chill
        extra="ignore",
    )

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "System Rebellion"

    # Server
    SERVER_NAME: str = "System Rebellion"
    SERVER_HOST: str = os.getenv("SERVER_HOST", "http://127.0.0.1:8000")

    # CORS: can be JSON list or comma-separated string
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]

    # Database
    DATABASE_URL: str | None = None
    SQLALCHEMY_DATABASE_URI: str = ""  # derived below

    # Security / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "system-rebellion-fixed-secret-key-for-development-only")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # 1h default
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Environment flags
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in {"1", "true", "yes", "on"}

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: Union[str, List[str]]) -> List[str]:
        # Accept either JSON-style list or plain comma-separated string
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                import json
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        return [str(i).strip() for i in parsed]
                except Exception:
                    pass
            # Fallback: comma separated
            return [i.strip() for i in s.split(",") if i.strip()]
        return []

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def derive_db_uri(cls, v: str, info: ValidationInfo) -> str:
        # Prefer explicit DATABASE_URL; otherwise default sqlite aiosqlite
        data = info.data or {}
        db_url = data.get("DATABASE_URL") or os.getenv("DATABASE_URL")
        if db_url and db_url.strip():
            return db_url.strip()
        return "sqlite+aiosqlite:///./system_rebellion.db"


settings = Settings()

