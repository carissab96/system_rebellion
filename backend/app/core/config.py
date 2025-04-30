import secrets
import os
from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    # Use a fixed SECRET_KEY for consistent token validation
    # In production, this should be set via environment variable
    SECRET_KEY: str = os.getenv("SECRET_KEY", "system-rebellion-fixed-secret-key-for-development-only")
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "System Rebellion"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: ["http://localhost", "http://localhost:4200", "http://localhost:3000"]
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "System Rebellion"
    
    # Database settings
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./system_rebellion.db"
    
    # JWT settings
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True


settings = Settings()
