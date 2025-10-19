# 環境変数だけを読む。ファイル（.env）は使わない。
import os
from typing import Optional


class Settings:
    # 単一URLで渡すか、個別項目で渡すかの両対応
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "app")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_SSLMODE: str = os.getenv(
        "DB_SSLMODE", "disable"
    )  # disable/require/verify-full など

    APP_ENV: str = os.getenv("APP_ENV", "dev")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    def database_url(self) -> str:
        # 優先：DATABASE_URL（psycopg v3 のドライバ名は "postgresql+psycopg"）
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # 個別項目からURLを合成
        # 例: postgresql+psycopg://user:pass@host:5432/dbname?sslmode=disable
        from urllib.parse import quote_plus

        user = quote_plus(self.DB_USER)
        pwd = quote_plus(self.DB_PASSWORD)
        return (
            f"postgresql+psycopg://{user}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?sslmode={self.DB_SSLMODE}"
        )


settings = Settings()
