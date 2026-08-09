from fastapi import Header, HTTPException, Depends, Cookie
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import uuid4
from jose import jwt, JWTError
from app.core.config import config

ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    data["sub"] = str(data["sub"])
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=config.ACCESS_TOKEN_EXPIRES_SECONDS
    )
    to_encode.update(
        {
            "exp": expire,
            "type": "access",
            "jti": str(uuid4()),
        }
    )
    return jwt.encode(to_encode, config.ACCESS_TOKEN_SECRET, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    data["sub"] = str(data["sub"])
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=config.REFRESH_TOKEN_EXPIRES_SECONDS
    )
    to_encode.update(
        {
            "exp": expire,
            "type": "refresh",
            "jti": str(uuid4()),
        }
    )
    return jwt.encode(to_encode, config.REFRESH_TOKEN_SECRET, algorithm=ALGORITHM)


def create_token_pair(account_id: int | str) -> Tuple[str, str]:
    data = {"sub": str(account_id)}
    return create_access_token(data), create_refresh_token(data)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, config.ACCESS_TOKEN_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, config.REFRESH_TOKEN_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None


def verify_access_token(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
        )

    return payload


def verify_refresh_token(refresh_token: Optional[str] = Cookie(None)) -> dict:
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Missing refresh token",
        )

    payload = decode_refresh_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    return payload


def get_account_id(payload: dict = Depends(verify_access_token)) -> int:
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        return int(sub)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subject format")
