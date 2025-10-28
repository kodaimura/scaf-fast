import os
from typing import Optional
from urllib.parse import quote_plus


class Settings:
    # === Database設定 ===
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "app")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_SSLMODE: str = os.getenv("DB_SSLMODE", "disable")

    # === アプリ環境設定 ===
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # === 認証関連設定 ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # === DB接続URLを返す ===
    def database_url(self) -> str:
        # 優先：DATABASE_URL
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # 個別項目からURLを合成
        user = quote_plus(self.DB_USER)
        pwd = quote_plus(self.DB_PASSWORD)
        return (
            f"postgresql+psycopg://{user}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?sslmode={self.DB_SSLMODE}"
        )


settings = Settings()
