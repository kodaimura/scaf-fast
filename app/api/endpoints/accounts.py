from fastapi import APIRouter, Depends, Response, Cookie, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.response import ApiResponse
from app.core.jwt import verify_access_token, create_token_pair, decode_token, create_access_token
from app.module.account.service import AccountService
from app.module.account.schemas import AccountCreateDto
from app.module.blacklist.service import BlacklistService
from app.module.blacklist.schemas import BlacklistAddDto

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
def signup(
    request: SignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    account_service = AccountService(db)

    account = account_service.create(
        AccountCreateDto(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            password=request.password,
        )
    )

    data = SignupResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.created(data=data, response=response)


# ---------------------------
# ログイン
# ---------------------------
@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    account_service = AccountService(db)
    account = account_service.authenticate(request.email, request.password)

    # JWTペア発行
    access_token, refresh_token = create_token_pair(str(account.id))

    # Cookieにrefreshトークンを設定
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # 本番では True に
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
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    jti = payload.get("jti")
    sub = payload.get("sub")

    if not jti or not sub:
        raise HTTPException(status_code=400, detail="Malformed token")

    blacklist_service = BlacklistService()

    # ブラックリスト登録済みなら無効
    if blacklist_service.is_revoked(jti):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    # access_token のみ再発行（refreshは再利用）
    access_token = create_access_token({"sub": sub})

    data = RefreshResponse(access_token=access_token)
    return ApiResponse.ok(data=data, response=response)



# ---------------------------
# ログアウト（ここでのみブラックリスト登録）
# ---------------------------
@router.post("/logout", response_model=LogoutResponse)
def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
):
    blacklist_service = BlacklistService()

    if refresh_token:
        payload = decode_token(refresh_token)
        if payload and payload.get("type") == "refresh":
            jti = payload.get("jti")
            exp = payload.get("exp")

            if jti and exp:
                dto = BlacklistAddDto(
                    jti=jti,
                    expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
                )
                blacklist_service.add(dto)

    # Cookie削除
    response.delete_cookie("refresh_token")

    return ApiResponse.ok(data=LogoutResponse(), response=response)


# ---------------------------
# アカウント情報取得（me）
# ---------------------------
@router.get("/me", response_model=MeResponse)
def get_me(
    response: Response,
    payload: dict = Depends(verify_access_token),
    db: Session = Depends(get_db),
):
    account_service = AccountService(db)
    account = account_service.get_by_id(int(payload["sub"]))

    data = MeResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.ok(data=data, response=response)
