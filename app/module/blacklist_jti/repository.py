from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from .model import BlacklistJti


class BlacklistJtiRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity: BlacklistJti) -> BlacklistJti:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def exists(self, jti: str) -> bool:
        stmt = select(BlacklistJti).where(BlacklistJti.jti == jti)
        return self.db.scalars(stmt).first() is not None

    def delete_expired(self) -> int:
        stmt = delete(BlacklistJti).where(BlacklistJti.expires_at < datetime.utcnow())
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount
