from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # ==========================
    # App
    # ==========================
    APP_NAME: str = "Papeleria API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ==========================
    # Database
    # ==========================
    DATABASE_URL: str

    # ==========================
    # Security / Auth
    # ==========================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ==========================
    # CORS
    # ==========================
    ALLOWED_ORIGINS: List[str] = []

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
