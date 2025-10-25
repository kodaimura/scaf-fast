from fastapi import APIRouter, Depends, Response, Cookie, status
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.response import ApiResponse
from modules.account.service import AccountService
from modules.refresh_token.service import RefreshTokenService
from modules.account.schemas import (
    AccountCreate,
    LoginRequest,
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


# ---------------------------
# サインアップ
# ---------------------------
@router.post("/signup", response_model=ApiResponse)
def signup(data: AccountCreate, response: Response, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    account = account_service.create(data)
    return ApiResponse.created(
        data={"account": account},
        message="Account created successfully",
        response=response,
    )


# ---------------------------
# ログイン
# ---------------------------
@router.post("/login", response_model=ApiResponse)
def login(response: Response, data: LoginRequest, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    refresh_service = RefreshTokenService(db)

    account = account_service.authenticate(data.email, data.password)
    if not account:
        return ApiResponse.error("Invalid email or password", response=response)

    access_token = refresh_service.issue(account.id)

    # Cookieにrefresh_tokenを保存
    response.set_cookie(
        key="refresh_token",
        value=access_token,
        httponly=True,
        secure=False,  # 本番では True
        samesite="lax",
        path="/accounts/refresh",
    )

    return ApiResponse.ok(
        data={"account": account, "access_token": access_token},
        message="Login successful",
        response=response,
    )


# ---------------------------
# トークンリフレッシュ
# ---------------------------
@router.post("/refresh", response_model=ApiResponse)
def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        return ApiResponse.unauthorized("Missing refresh token", response=response)

    token_service = RefreshTokenService(db)
    token_data = token_service.get_valid_token(refresh_token)
    if not token_data:
        return ApiResponse.unauthorized("Invalid or expired token", response=response)

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

    return ApiResponse.ok(
        data={"account": account, "access_token": new_token},
        message="Token refreshed",
        response=response,
    )


# ---------------------------
# ログアウト
# ---------------------------
@router.post("/logout", response_model=ApiResponse)
def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    token_service = RefreshTokenService(db)

    if refresh_token:
        token_service.revoke(refresh_token)

    response.delete_cookie("refresh_token")

    return ApiResponse.ok(message="Logged out successfully", response=response)


# ---------------------------
# アカウント情報取得（me）
# ---------------------------
@router.get("/me", response_model=ApiResponse)
def get_me(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        return ApiResponse.unauthorized("Not authenticated", response=response)

    token_service = RefreshTokenService(db)
    token_data = token_service.get_valid_token(refresh_token)
    if not token_data:
        return ApiResponse.unauthorized("Invalid token", response=response)

    account_service = AccountService(db)
    account = account_service.get_by_id(token_data.account_id)
    if not account:
        return ApiResponse.not_found("Account not found", response=response)

    return ApiResponse.ok(data={"account": account}, response=response)
