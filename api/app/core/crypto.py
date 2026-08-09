import bcrypt
import hashlib
import secrets
from datetime import datetime, timedelta


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token() -> str:
    return secrets.token_urlsafe(64)


def generate_expiry(hours: int = 24) -> datetime:
    return datetime.utcnow() + timedelta(hours=hours)
