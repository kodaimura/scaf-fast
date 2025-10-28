from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.response import ApiResponse
from app.core.crypto import hash_password, verify_password
from app.core.jwt import get_current_user
from app.module.account.service import AccountService
from app.module.account.schemas import AccountCreateDto
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
def signup(request: SignupRequest, response: Response, db: Session = Depends(get_db)):
    account_service = AccountService(db)

    account = account_service.create(AccountCreateDto(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        password_hash=hash_password(request.password),
    ))

    data = SignupResponse(
        account=AccountResponse.from_orm(account)
    )

    return ApiResponse.created(data=data, response=response)


# ---------------------------
# ログイン
# ---------------------------
@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    refresh_service = RefreshTokenService(db)

    account = account_service.get_by_email(request.email)
    if not account or not verify_password(request.password, account.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = refresh_service.issue(account.id)

    response.set_cookie(
        key="refresh_token",
        value=access_token,
        httponly=True,
        secure=False,  # 本番では True
        samesite="lax",
        path="/",
    )

    data = LoginResponse(
        account=AccountResponse.from_orm(account),
        access_token=access_token,
    )

    return ApiResponse.ok(data=data, response=response)


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
        secure=False,  # 本番では True
        samesite="lax",
        path="/",
    )

    account_service = AccountService(db)
    account = account_service.get_by_id(token_data.account_id)

    data = RefreshResponse(
        account=AccountResponse.from_orm(account),
        access_token=new_token,
    )

    return ApiResponse.ok(data=data, response=response)


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
    data = LogoutResponse()
    return ApiResponse.ok(data=data, response=response)


# ---------------------------
# アカウント情報取得（me）
# ---------------------------
@router.get("/me", response_model=MeResponse)
def get_me(
    response: Response,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account_service = AccountService(db)
    account = account_service.get_by_id(payload["sub"])

    data = MeResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.ok(data=data, response=response)

