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
    """
    ユーザーのパスワードをハッシュ化
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    平文とハッシュを照合
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # bcryptは72バイトを超えるパスワードでエラーになる
        return False


# ======== JWTトークン関連 ======== #
def create_access_token(data: dict) -> str:
    """
    アクセストークン（短期有効）
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    リフレッシュトークン（長期有効）
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_token_pair(user_id: str) -> Tuple[str, str]:
    """
    アクセストークン + リフレッシュトークンを同時発行
    """
    token_data = {"sub": user_id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return access_token, refresh_token


def decode_token(token: str) -> Optional[dict]:
    """
    トークンを復号してペイロードを返す
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    トークン種別（access / refresh）の整合性を確認
    """
    payload = decode_token(token)
    if not payload:
        return False
    return payload.get("type") == expected_type


# ======== DB用リフレッシュトークン生成 ======== #
def generate_token() -> str:
    """
    DB保存型リフレッシュトークン（JWTではなく純粋なランダム文字列）
    """
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    """
    リフレッシュトークンをハッシュ化して保存するための関数。
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_expiry(hours: int = 24) -> datetime:
    """
    リフレッシュトークンの有効期限を生成（デフォルト24時間）
    """
    return datetime.utcnow() + timedelta(hours=hours)
