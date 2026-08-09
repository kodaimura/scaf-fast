from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.jwt import get_account_id
from app.core.response import ApiResponse
from app.handler.dto.accounts import AccountResponse, GetCurrentAccountResponse
from app.usecase.accounts.get_current import GetCurrentAccountInput, GetCurrentAccountUsecase

router = APIRouter()


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
