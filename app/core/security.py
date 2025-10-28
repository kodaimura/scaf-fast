from fastapi import HTTPException, status, Header, Depends
from datetime import datetime, timedelta
from typing import Tuple, Optional
from jose import jwt, JWTError
import bcrypt
import secrets
import hashlib
from app.core.config import settings

# JWTアルゴリズム
ALGORITHM = "HS256"


# ======== パスワード関連 ======== #
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # bcryptは72バイトを超えるパスワードでエラーになる
        return False


# ======== JWTトークン関連 ======== #
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_token_pair(user_id: str) -> Tuple[str, str]:
    token_data = {"sub": user_id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return access_token, refresh_token


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    payload = decode_token(token)
    if not payload:
        return False
    return payload.get("type") == expected_type


def verify_access_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload or not verify_token_type(token, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    return payload


# ======== DB用リフレッシュトークン生成 ======== #
def generate_token() -> str:
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_expiry(hours: int = 24) -> datetime:
    return datetime.utcnow() + timedelta(hours=hours)


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI依存関数として使えるJWT検証関数。
    成功すればpayloadを返し、失敗時はHTTPExceptionをraiseする。
    """
    payload = verify_access_token(authorization)
    return payload