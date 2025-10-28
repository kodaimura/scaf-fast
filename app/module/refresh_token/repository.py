from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.crypto import hash_token
from .model import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity: RefreshToken) -> RefreshToken:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_by_token(self, token: str) -> RefreshToken | None:
        token_hash = hash_token(token)
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.scalars(stmt).first()

    def update(self, entity: RefreshToken) -> RefreshToken:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
