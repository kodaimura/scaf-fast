from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.jwt import verify_access_token
from app.service.auth import validate_access_token_account


def get_account_id(
    request: Request,
    payload: dict = Depends(verify_access_token),
    db: Session = Depends(get_db),
) -> int:
    account_id = validate_access_token_account(db, payload)
    request.state.account_id = account_id
    return account_id
