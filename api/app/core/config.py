import os


class Config:
    # === アプリ環境設定 ===
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_SIGNUP: bool = os.getenv("ENABLE_SIGNUP", "true").lower() == "true"
    AUTH_LOGIN_ID_MODE: str = os.getenv("AUTH_LOGIN_ID_MODE", "email").lower()
    FRONTEND_ORIGINS: list[str] = os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # === Database設定 ===
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@db:5432/project_db?sslmode=disable",
    )

    # === 認証関連設定 ===
    ACCESS_TOKEN_SECRET: str = os.getenv("ACCESS_TOKEN_SECRET", "randomstring")
    ACCESS_TOKEN_EXPIRES_SECONDS: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRES_SECONDS", 900)
    )
    REFRESH_TOKEN_SECRET: str = os.getenv("REFRESH_TOKEN_SECRET", "randomstring")
    REFRESH_TOKEN_EXPIRES_SECONDS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRES_SECONDS", 2592000)
    )
    REFRESH_TOKEN_REMEMBER_ME_EXPIRES_SECONDS: int = int(
        os.getenv("REFRESH_TOKEN_REMEMBER_ME_EXPIRES_SECONDS", 2592000)
    )

    # === パスワード再設定 ===
    PASSWORD_RESET_URL_BASE: str = os.getenv(
        "PASSWORD_RESET_URL_BASE",
        "http://localhost:3000/reset-password",
    )
    PASSWORD_RESET_TOKEN_EXPIRES_MINUTES: int = int(
        os.getenv("PASSWORD_RESET_TOKEN_EXPIRES_MINUTES", 30)
    )
    PASSWORD_RESET_RESEND_INTERVAL_MINUTES: int = int(
        os.getenv("PASSWORD_RESET_RESEND_INTERVAL_MINUTES", 5)
    )

    # === Mail ===
    MAIL_FROM: str = os.getenv("MAIL_FROM", "no-reply@example.local")
    SMTP_HOST: str | None = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str | None = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"


config = Config()
