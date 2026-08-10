from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse
from app.handler._dependency import get_account_id
from app.handler.dto.accounts import (
    AccountResponse,
    GetAccountResponse,
    GetAccountsResponse,
    GetCurrentAccountResponse,
    PostAccountRequest,
    PostAccountResponse,
    PutAccountDisableResponse,
    PutAccountEnableResponse,
    PutAccountRequest,
    PutAccountResponse,
)
from app.usecase.accounts.create import CreateAccountInput, CreateAccountUsecase
from app.usecase.accounts.disable import DisableAccountInput, DisableAccountUsecase
from app.usecase.accounts.enable import EnableAccountInput, EnableAccountUsecase
from app.usecase.accounts.get import GetAccountInput, GetAccountUsecase
from app.usecase.accounts.get_current import GetCurrentAccountInput, GetCurrentAccountUsecase
from app.usecase.accounts.list import ListAccountsUsecase
from app.usecase.accounts.update import UpdateAccountInput, UpdateAccountUsecase

router = APIRouter()


@router.get("/accounts", response_model=GetAccountsResponse)
def get_accounts(
    response: Response,
    account_id: int = Depends(get_account_id),
    db: Session = Depends(get_db),
):
    _ = account_id
    usecase = ListAccountsUsecase(db)
    accounts = usecase.execute()
    data = GetAccountsResponse(
        accounts=[AccountResponse.from_orm(account) for account in accounts]
    )
    return ApiResponse.ok(data=data, response=response)


@router.post("/accounts", response_model=PostAccountResponse)
def post_account(
    request: PostAccountRequest,
    response: Response,
    account_id: int = Depends(get_account_id),
    db: Session = Depends(get_db),
):
    _ = account_id
    usecase = CreateAccountUsecase(db)
    account = usecase.execute(
        CreateAccountInput(
            login_id=request.login_id,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )
    )
    data = PostAccountResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.created(data=data, response=response)


@router.get("/accounts/me", response_model=GetCurrentAccountResponse)
def get_current_account(
    response: Response,
    account_id: int = Depends(get_account_id),
    db: Session = Depends(get_db),
):
    usecase = GetCurrentAccountUsecase(db)
    account = usecase.execute(GetCurrentAccountInput(account_id=account_id))
    data = GetCurrentAccountResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.ok(data=data, response=response)


@router.get("/accounts/{target_account_id}", response_model=GetAccountResponse)
def get_account(
    target_account_id: int,
    response: Response,
    account_id: int = Depends(get_account_id),
    db: Session = Depends(get_db),
):
    _ = account_id
    usecase = GetAccountUsecase(db)
    account = usecase.execute(GetAccountInput(account_id=target_account_id))
    data = GetAccountResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.ok(data=data, response=response)


@router.put("/accounts/{target_account_id}", response_model=PutAccountResponse)
def put_account(
    target_account_id: int,
    request: PutAccountRequest,
    response: Response,
    account_id: int = Depends(get_account_id),
    db: Session = Depends(get_db),
):
    _ = account_id
    usecase = UpdateAccountUsecase(db)
    account = usecase.execute(
        UpdateAccountInput(
            account_id=target_account_id,
            login_id=request.login_id,
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            password=request.password,
        )
    )
    data = PutAccountResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.ok(data=data, response=response)


@router.put(
    "/accounts/{target_account_id}/disable",
    response_model=PutAccountDisableResponse,
)
def put_account_disable(
    target_account_id: int,
    response: Response,
    account_id: int = Depends(get_account_id),
    db: Session = Depends(get_db),
):
    _ = account_id
    usecase = DisableAccountUsecase(db)
    account = usecase.execute(DisableAccountInput(account_id=target_account_id))
    data = PutAccountDisableResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.ok(data=data, response=response)


@router.put(
    "/accounts/{target_account_id}/enable",
    response_model=PutAccountEnableResponse,
)
def put_account_enable(
    target_account_id: int,
    response: Response,
    account_id: int = Depends(get_account_id),
    db: Session = Depends(get_db),
):
    _ = account_id
    usecase = EnableAccountUsecase(db)
    account = usecase.execute(EnableAccountInput(account_id=target_account_id))
    data = PutAccountEnableResponse(account=AccountResponse.from_orm(account))
    return ApiResponse.ok(data=data, response=response)
