import os
from typing import Optional
from urllib.parse import quote_plus


class Settings:
    # === アプリ環境設定 ===
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # === Database設定 ===
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@db:5432/project_db?sslmode=disable",
    )

    # === Redis設定 ===
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # === 認証関連設定 ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


settings = Settings()
