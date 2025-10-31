from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import config
from app.core.database import get_db
from app.core.response import ApiResponse
from app.core.jwt import (
    get_account_id,
    verify_refresh_token,
)
from app.usecases.account.signup import SignupUsecase, SignupInput
from app.usecases.account.login import LoginUsecase, LoginInput
from app.usecases.account.refresh import RefreshUsecase, RefreshInput
from app.usecases.account.logout import LogoutUsecase, LogoutInput
from app.usecases.account.get_me import GetMeUsecase, GetMeInput

from .dto.accounts import (
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


@router.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest, response: Response, db: Session = Depends(get_db)):
    usecase = SignupUsecase(db)
    account = usecase.execute(
        SignupInput(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )
    )
    data = SignupResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.created(data=data, response=response)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    usecase = LoginUsecase(db)
    result = usecase.execute(LoginInput(email=request.email, password=request.password))

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=(config.APP_ENV == "production"),
        samesite="lax",
        path="/",
    )

    data = LoginResponse(
        account=AccountResponse.from_orm(result.account),
        access_token=result.access_token,
    )

    return ApiResponse.ok(data=data, response=response)


@router.post("/refresh", response_model=RefreshResponse)
def refresh_token(response: Response, payload: dict = Depends(verify_refresh_token)):
    usecase = RefreshUsecase()
    result = usecase.execute(
        RefreshInput(
            jti=payload.get("jti"),
            sub=payload.get("sub"),
        )
    )
    data = RefreshResponse(access_token=result.access_token)
    return ApiResponse.ok(data=data, response=response)


@router.post("/logout", response_model=LogoutResponse)
def logout(response: Response, payload: dict = Depends(verify_refresh_token)):
    usecase = LogoutUsecase()
    input = LogoutInput(jti=payload.get("jti"), exp=payload.get("exp"))
    usecase.execute(input)

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=(config.APP_ENV == "production"),
        samesite="lax",
        path="/",
    )

    return ApiResponse.ok(data=LogoutResponse(), response=response)


@router.get("/me", response_model=MeResponse)
def get_me(
    response: Response,
    account_id: int = Depends(get_account_id),
    db: Session = Depends(get_db),
):
    usecase = GetMeUsecase(db)
    input = GetMeInput(account_id=account_id)

    account = usecase.execute(input)
    data = MeResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.ok(data=data, response=response)
