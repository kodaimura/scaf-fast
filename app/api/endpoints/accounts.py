from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from core.database import get_db
from core.security import hash_token
from modules.account.service import AccountService
from modules.refresh_token.service import RefreshTokenService
from modules.account.schemas import (
    AccountCreate,
    LoginRequest,
    LoginResponse,
    AccountResponse,
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


# ---------------------------
# サインアップ
# ---------------------------
@router.post("/signup", response_model=AccountResponse)
def signup(data: AccountCreate, db: Session = Depends(get_db)):
    service = AccountService(db)
    return service.create(data)


# ---------------------------
# ログイン
# ---------------------------
@router.post("/login", response_model=LoginResponse)
def login(response: Response, data: LoginRequest, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    token_service = RefreshTokenService(db)

    account = account_service.authenticate(data.email, data.password)
    access_token = token_service.issue(account.id)

    # Cookieにrefresh_tokenを保存
    response.set_cookie(
        key="refresh_token",
        value=access_token,
        httponly=True,
        secure=False,  # 本番はTrue
        samesite="lax",
        path="/accounts/refresh",
    )

    return {"account": account, "access_token": access_token}


# ---------------------------
# トークンリフレッシュ
# ---------------------------
@router.post("/refresh", response_model=LoginResponse)
def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    token_service = RefreshTokenService(db)
    token_data = token_service.get_valid_token(refresh_token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # 新しいトークンを発行
    new_token = token_service.issue(token_data.account_id)
    response.set_cookie(
        key="refresh_token",
        value=new_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/accounts/refresh",
    )

    account_service = AccountService(db)
    account = account_service.get_by_id(token_data.account_id)
    return {"account": account, "access_token": new_token}


# ---------------------------
# ログアウト
# ---------------------------
@router.post("/logout")
def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    token_service = RefreshTokenService(db)

    if refresh_token:
        token_service.revoke(refresh_token)

    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}


# ---------------------------
# アカウント情報取得（me）
# ---------------------------
@router.get("/me", response_model=AccountResponse)
def get_me(
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_service = RefreshTokenService(db)
    token_data = token_service.get_valid_token(refresh_token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    account_service = AccountService(db)
    account = account_service.get_by_id(token_data.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account
