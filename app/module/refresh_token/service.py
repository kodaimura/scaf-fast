from sqlalchemy.orm import Session
from core.security import generate_token, generate_expiry
from .repository import RefreshTokenRepository


class RefreshTokenService:
    def __init__(self, db: Session):
        self.repo = RefreshTokenRepository(db)

    def issue(self, account_id: int) -> str:
        token = generate_token()
        expiry = generate_expiry(24)
        self.repo.create(account_id, token, expiry)
        return token

    def revoke(self, token: str) -> bool:
        return self.repo.revoke(token)

    def get_valid_token(self, token: str):
        """有効なトークンを返す（無効ならNone）"""
        token_obj = self.repo.get_by_token(token)
        if not token_obj:
            return None
        if not self.repo.is_valid(token):
            return None
        return token_obj
