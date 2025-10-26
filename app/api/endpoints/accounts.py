from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.response import ApiResponse
from app.module.account.service import AccountService
from app.module.refresh_token.service import RefreshTokenService

from app.api.dto.accounts import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    RefreshResponse,
    LogoutResponse,
    MeResponse,
    AccountResponse,
)

router = APIRouter()


# ---------------------------
# サインアップ
# ---------------------------
@router.post("/signup", response_model=SignupResponse)
def signup(data: SignupRequest, response: Response, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    account_internal = account_service.create(data)
    account_data = AccountResponse.model_validate(account_internal.model_dump())
    response_dto = SignupResponse(account=account_data)

    return ApiResponse.created(
        data=response_dto.model_dump(),
        response=response,
    )


# ---------------------------
# ログイン
# ---------------------------
@router.post("/login", response_model=LoginResponse)
def login(response: Response, data: LoginRequest, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    refresh_service = RefreshTokenService(db)

    account_internal = account_service.authenticate(data.email, data.password)
    access_token = refresh_service.issue(account_internal.id)

    response.set_cookie(
        key="refresh_token",
        value=access_token,
        httponly=True,
        secure=False,  # 本番ではTrue
        samesite="lax",
        path="/accounts/refresh",
    )

    account_data = AccountResponse.model_validate(account_internal.model_dump())
    response_dto = LoginResponse(account=account_data, access_token=access_token)

    return ApiResponse.ok(
        data=response_dto.model_dump(),
        response=response,
    )


# ---------------------------
# トークンリフレッシュ
# ---------------------------
@router.post("/refresh", response_model=RefreshResponse)
def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        return ApiResponse.unauthorized("Missing refresh token")

    token_service = RefreshTokenService(db)
    token_data = token_service.get_valid_token(refresh_token)
    if not token_data:
        return ApiResponse.unauthorized("Invalid or expired token")

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
    account_internal = account_service.get_by_id(token_data.account_id)
    account_data = AccountResponse.model_validate(account_internal.model_dump())

    response_dto = RefreshResponse(account=account_data, access_token=new_token)
    return ApiResponse.ok(data=response_dto.model_dump(), response=response)


# ---------------------------
# ログアウト
# ---------------------------
@router.post("/logout", response_model=LogoutResponse)
def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    token_service = RefreshTokenService(db)
    if refresh_token:
        token_service.revoke(refresh_token)

    response.delete_cookie("refresh_token")
    response_dto = LogoutResponse()
    return ApiResponse.ok(data=response_dto.model_dump(), response=response)


# ---------------------------
# アカウント情報取得（me）
# ---------------------------
@router.get("/me", response_model=MeResponse)
def get_me(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        return ApiResponse.unauthorized("Not authenticated")

    token_service = RefreshTokenService(db)
    token_data = token_service.get_valid_token(refresh_token)
    if not token_data:
        return ApiResponse.unauthorized("Invalid token")

    account_service = AccountService(db)
    account_internal = account_service.get_by_id(token_data.account_id)
    account_data = AccountResponse.model_validate(account_internal.model_dump())

    response_dto = MeResponse(account=account_data)
    return ApiResponse.ok(data=response_dto.model_dump(), response=response)
