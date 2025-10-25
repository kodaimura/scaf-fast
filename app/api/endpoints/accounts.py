from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from domain.accounts import schemas, service

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=schemas.AccountRead)
def create_account(data: schemas.AccountCreate, db: Session = Depends(get_db)):
    svc = service.AccountService(db)
    return svc.create_account(data)


@router.get("/{account_id}", response_model=schemas.AccountRead)
def get_account(account_id: int, db: Session = Depends(get_db)):
    svc = service.AccountService(db)
    return svc.get_account(account_id)


@router.get("/", response_model=list[schemas.AccountRead])
def list_accounts(db: Session = Depends(get_db)):
    svc = service.AccountService(db)
    return svc.list_accounts()


@router.put("/{account_id}", response_model=schemas.AccountRead)
def update_account(
    account_id: int, data: schemas.AccountUpdate, db: Session = Depends(get_db)
):
    svc = service.AccountService(db)
    return svc.update_account(account_id, data)


@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    svc = service.AccountService(db)
    return svc.delete_account(account_id)
