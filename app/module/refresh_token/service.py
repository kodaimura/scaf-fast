from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session
from app.core.config import settings
from .repository import RefreshTokenRepository


class RefreshTokenService:
    """
    リフレッシュトークンの発行・検証・失効管理
    """

    def __init__(self, db: Session):
        self.repo = RefreshTokenRepository(db)

    # ==== トークン生成関連 ==== #
    def generate_token(self) -> str:
        """
        ランダムなトークン文字列を生成（DB保存用のリフレッシュトークン）
        """
        return secrets.token_urlsafe(64)  # 高強度ランダムトークン

    def generate_expiry(
        self, days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS
    ) -> datetime:
        """
        有効期限を生成（デフォルトは設定値）
        """
        return datetime.utcnow() + timedelta(days=days)

    # ==== トークン発行 ==== #
    def issue(self, account_id: int) -> str:
        """
        新しいリフレッシュトークンを発行し、DBに保存
        """
        token = self.generate_token()
        expiry = self.generate_expiry()
        self.repo.create(account_id, token, expiry)
        return token

    # ==== トークン失効 ==== #
    def revoke(self, token: str) -> bool:
        """
        トークンを失効状態に更新
        """
        return self.repo.revoke(token)

    # ==== トークン検証 ==== #
    def get_valid_token(self, token: str):
        """
        有効なトークンを返す（無効または期限切れならNone）
        """
        token_obj = self.repo.get_by_token(token)
        if not token_obj:
            return None

        # 無効フラグ・期限切れチェック
        if token_obj.revoked:
            return None
        if token_obj.expires_at < datetime.utcnow():
            return None

        return token_obj
