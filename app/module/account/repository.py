from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from .model import Account
from .schemas import AccountCreate


class AccountRepository:
    """AccountモデルのDB操作専用リポジトリ"""

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------
    # 作成
    # ---------------------------
    def create(self, data: AccountCreate, password_hash: str) -> Account:
        """新規アカウント作成"""
        account = Account(
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    # ---------------------------
    # 取得
    # ---------------------------
    def get_by_email(self, email: str) -> Optional[Account]:
        """メールアドレスで取得"""
        stmt = select(Account).where(
            Account.email == email, Account.deleted_at.is_(None)
        )
        return self.db.scalars(stmt).first()

    def get_by_id(self, account_id: int) -> Optional[Account]:
        """IDで取得"""
        stmt = select(Account).where(
            Account.id == account_id, Account.deleted_at.is_(None)
        )
        return self.db.scalars(stmt).first()

    # ---------------------------
    # 論理削除
    # ---------------------------
    def soft_delete(self, account_id: int) -> bool:
        """アカウント論理削除"""
        account = self.get_by_id(account_id)
        if not account:
            return False
        account.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
