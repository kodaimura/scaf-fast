from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session
from app.core.config import settings
from .repository import RefreshTokenRepository


class RefreshTokenService:
    def __init__(self, db: Session):
        self.repo = RefreshTokenRepository(db)

    # ==== トークン生成関連 ==== #
    def generate_token(self) -> str:
        return secrets.token_urlsafe(64)
    
    def generate_expiry(
        self, days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS
    ) -> datetime:
        return datetime.utcnow() + timedelta(days=days)

    # ==== トークン発行 ==== #
    def issue(self, account_id: int) -> str:
        token = self.generate_token()
        expiry = self.generate_expiry()
        self.repo.create(account_id, token, expiry)
        return token

    # ==== トークン失効 ==== #
    def revoke(self, token: str) -> bool:
        return self.repo.revoke(token)

    # ==== トークン検証 ==== #
    def get_valid_token(self, token: str):
        token_obj = self.repo.get_by_token(token)
        if not token_obj:
            return None

        # 無効フラグ・期限切れチェック
        if token_obj.revoked_at:
            return None
        if token_obj.expires_at < datetime.utcnow():
            return None

        return token_obj
