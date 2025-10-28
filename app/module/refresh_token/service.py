from datetime import datetime
from sqlalchemy.orm import Session
from app.core.crypto import generate_token, generate_expiry
from app.module.refresh_token.repository import RefreshTokenRepository


class RefreshTokenService:
    def __init__(self, db: Session):
        self.repo = RefreshTokenRepository(db)

    def issue(self, account_id: int) -> str:
        token = generate_token()
        expiry = generate_expiry(hours=24 * 7)
        self.repo.create(account_id, token, expiry)
        return token

    def revoke(self, token: str) -> bool:
        token_obj = self.repo.get_by_token(token)
        if not token_obj:
            return False

        token_obj.revoked_at = datetime.utcnow()
        self.repo.update(token_obj)
        return True

    def get_valid_token(self, token: str):
        token_obj = self.repo.get_by_token(token)
        if not token_obj:
            return None

        if token_obj.revoked_at or token_obj.expires_at < datetime.utcnow():
            return None

        return token_obj
