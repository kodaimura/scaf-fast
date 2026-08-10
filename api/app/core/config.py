import os


def _get_choice(name: str, default: str, choices: set[str]) -> str:
    value = os.getenv(name, default).strip().lower()
    if value not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"{name} must be one of: {allowed}")
    return value


def _get_bool(name: str, default: bool) -> bool:
    default_value = "true" if default else "false"
    value = os.getenv(name, default_value).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


def _get_required_production_secret(name: str, app_env: str) -> str:
    value = os.getenv(name, "randomstring")
    if app_env == "production" and value == "randomstring":
        raise ValueError(f"{name} must be changed for production")
    if app_env == "production" and not value.strip():
        raise ValueError(f"{name} must not be empty for production")
    return value


class Config:
    # === アプリ環境設定 ===
    APP_ENV: str = _get_choice("APP_ENV", "dev", {"dev", "production", "test"})
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_SIGNUP: bool = _get_bool("ENABLE_SIGNUP", True)
    AUTH_LOGIN_ID_MODE: str = _get_choice(
        "AUTH_LOGIN_ID_MODE", "email", {"email", "login_id"}
    )
    FRONTEND_ORIGINS: list[str] = os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # === Database設定 ===
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@db:5432/project_db?sslmode=disable",
    )

    # === 認証関連設定 ===
    ACCESS_TOKEN_SECRET: str = _get_required_production_secret(
        "ACCESS_TOKEN_SECRET", APP_ENV
    )
    ACCESS_TOKEN_EXPIRES_SECONDS: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRES_SECONDS", 900)
    )
    REFRESH_TOKEN_SECRET: str = _get_required_production_secret(
        "REFRESH_TOKEN_SECRET", APP_ENV
    )
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
    MAIL_PROVIDER: str = _get_choice("MAIL_PROVIDER", "mailhog", {"mailhog", "smtp"})
    MAIL_FROM: str = os.getenv("MAIL_FROM", "no-reply@example.local")
    SMTP_HOST: str | None = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str | None = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD")
    SMTP_USE_TLS: bool = _get_bool("SMTP_USE_TLS", True)

    if MAIL_PROVIDER == "smtp" and not SMTP_HOST:
        raise ValueError("SMTP_HOST is required when MAIL_PROVIDER=smtp")


config = Config()
