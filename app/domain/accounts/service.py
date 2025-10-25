from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from domain.accounts import repository, schemas


class AccountService:
    """アカウントに関するビジネスロジック層"""

    def __init__(self, db: Session):
        self.repo = repository.AccountRepository(db)

    # -----------------------------
    # Create
    # -----------------------------
    def create_account(self, data: schemas.AccountCreate):
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        return self.repo.create(data)

    # -----------------------------
    # Read
    # -----------------------------
    def get_account(self, account_id: int):
        account = self.repo.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    def list_accounts(self) -> List[schemas.AccountRead]:
        return self.repo.list()

    # -----------------------------
    # Update
    # -----------------------------
    def update_account(self, account_id: int, data: schemas.AccountUpdate):
        account = self.repo.update(account_id, data)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    # -----------------------------
    # Delete (論理削除)
    # -----------------------------
    def delete_account(self, account_id: int):
        success = self.repo.soft_delete(account_id)
        if not success:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"message": "Account deleted successfully"}
