from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from .repository import AccountRepository
from .schemas import AccountCreate, AccountInternal


class AccountService:
    """アカウント関連のビジネスロジック"""

    def __init__(self, db: Session):
        self.repo = AccountRepository(db)

    # ---------------------------
    # 作成
    # ---------------------------
    def create(self, data: AccountCreate) -> AccountInternal:
        """新規アカウント作成"""
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # ✅ サービス層でハッシュ化
        hashed_password = hash_password(data.password)

        account = self.repo.create(data, hashed_password)
        return AccountInternal.from_orm(account)

    # ---------------------------
    # 認証
    # ---------------------------
    def authenticate(self, email: str, password: str) -> AccountInternal:
        """メールとパスワードで認証"""
        account = self.repo.get_by_email(email)
        if not account or not verify_password(password, account.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return AccountInternal.from_orm(account)

    # ---------------------------
    # ID取得
    # ---------------------------
    def get_by_id(self, account_id: int) -> AccountInternal:
        """アカウントをIDで取得"""
        account = self.repo.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return AccountInternal.from_orm(account)
