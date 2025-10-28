from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.crypto import generate_token, generate_expiry, hash_token
from .model import RefreshToken
from .repository import RefreshTokenRepository
from app.core.config import settings


class RefreshTokenService:
    def __init__(self, db: Session):
        self.repo = RefreshTokenRepository(db)

    def issue(self, account_id: int) -> str:
        token_plain = generate_token()

        self.repo.create(RefreshToken(
            account_id=account_id,
            token_hash=hash_token(token_plain),
            issued_at=datetime.utcnow(),
            expires_at=generate_expiry(hours=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24),
        ))
        return token_plain

    def revoke(self, token_plain: str) -> None:
        token_hash = hash_token(token_plain)
        refresh_token = self.repo.get_by_token(token_hash)
        if not refresh_token:
            raise HTTPException(status_code=404, detail="Refresh token not found")

        refresh_token.revoked_at = datetime.utcnow()
        self.repo.update(refresh_token)

    def get_valid_token(self, token_plain: str) -> RefreshToken | None:
        token_hash = hash_token(token_plain)
        refresh_token = self.repo.get_by_token(token_hash)
        if not refresh_token:
            return None

        if refresh_token.revoked_at or refresh_token.expires_at < datetime.utcnow():
            return None

        return refresh_token
