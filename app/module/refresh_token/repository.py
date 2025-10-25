from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from core.security import hash_token
from .model import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = RefreshToken

    def create(self, account_id: int, token: str, expires_at: datetime) -> RefreshToken:
        token_hash = hash_token(token)
        refresh_token = RefreshToken(
            account_id=account_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token

    def get_by_token(self, token: str) -> RefreshToken | None:
        """平文のtokenからDB上のトークンを検索"""
        token_hash = hash_token(token)
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.scalars(stmt).first()

    def revoke(self, token: str) -> bool:
        token_obj = self.get_by_token(token)
        if not token_obj:
            return False
        token_obj.revoked_at = datetime.utcnow()
        self.db.commit()
        return True

    def is_valid(self, token: str) -> bool:
        token_obj = self.get_by_token(token)
        if not token_obj:
            return False
        if token_obj.revoked_at:
            return False
        if token_obj.expires_at and token_obj.expires_at < datetime.utcnow():
            return False
        return True
