import os


class Config:
    # === アプリ環境設定 ===
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    FRONTEND_ORIGINS: list[str] = os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # === Database設定 ===
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@db:5432/project_db?sslmode=disable",
    )

    # === Redis設定 ===
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # === 認証関連設定 ===
    ACCESS_TOKEN_SECRET: str = os.getenv("ACCESS_TOKEN_SECRET", "randomstring")
    ACCESS_TOKEN_EXPIRES_SECONDS: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRES_SECONDS", 900)
    )
    REFRESH_TOKEN_SECRET: str = os.getenv("REFRESH_TOKEN_SECRET", "randomstring")
    REFRESH_TOKEN_EXPIRES_SECONDS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRES_SECONDS", 2592000)
    )


config = Config()
