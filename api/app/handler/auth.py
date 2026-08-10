from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import config
from app.core.database import get_db
from app.core.error import AppError, ErrorCode
from app.core.jwt import verify_refresh_token
from app.core.response import ApiResponse
from app.handler.dto.auth import (
    AccountResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    SignupRequest,
    SignupResponse,
)
from app.usecase.auth.login import LoginInput, LoginUsecase
from app.usecase.auth.refresh import RefreshInput, RefreshUsecase
from app.usecase.auth.signup import SignupInput, SignupUsecase

router = APIRouter()


@router.post("/auth/signup", response_model=SignupResponse)
def signup(request: SignupRequest, response: Response, db: Session = Depends(get_db)):
    if not config.ENABLE_SIGNUP:
        raise AppError(code=ErrorCode.FORBIDDEN)

    usecase = SignupUsecase(db)
    account = usecase.execute(
        SignupInput(
            login_id=request.login_id,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )
    )
    data = SignupResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.created(data=data, response=response)


@router.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    usecase = LoginUsecase(db)
    result = usecase.execute(
        LoginInput(
            login_id=request.login_id,
            password=request.password,
            remember_me=request.remember_me,
        )
    )

    refresh_token_max_age = (
        config.REFRESH_TOKEN_REMEMBER_ME_EXPIRES_SECONDS
        if request.remember_me
        else config.REFRESH_TOKEN_EXPIRES_SECONDS
    )

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=(config.APP_ENV == "production"),
        samesite="lax",
        path="/",
        max_age=refresh_token_max_age,
    )

    data = LoginResponse(
        account=AccountResponse.from_orm(result.account),
        access_token=result.access_token,
    )
    return ApiResponse.ok(data=data, response=response)


@router.post("/auth/refresh", response_model=RefreshResponse)
def refresh_token(
    response: Response,
    payload: dict = Depends(verify_refresh_token),
    db: Session = Depends(get_db),
):
    usecase = RefreshUsecase(db)
    result = usecase.execute(
        RefreshInput(
            sub=payload.get("sub"),
            token_version=payload.get("token_version"),
        )
    )
    data = RefreshResponse(access_token=result.access_token)
    return ApiResponse.ok(data=data, response=response)


@router.post("/auth/logout", response_model=LogoutResponse)
def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=(config.APP_ENV == "production"),
        samesite="lax",
        path="/",
    )

    return ApiResponse.ok(data=LogoutResponse(), response=response)
