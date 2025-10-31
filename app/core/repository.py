from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T, soft: bool = True) -> bool:
        if not entity:
            return False
        if soft and hasattr(entity, "deleted_at"):
            entity.deleted_at = datetime.now(timezone.utc)
            self.db.flush()
        else:
            self.db.delete(entity)
        return True

    def get_one(self, entity: T) -> Optional[T]:
        stmt = select(self.model)
        conditions = []
        for attr, value in vars(entity).items():
            if value is not None and hasattr(self.model, attr):
                conditions.append(getattr(self.model, attr) == value)
        if hasattr(self.model, "deleted_at"):
            conditions.append(self.model.deleted_at.is_(None))
        if conditions:
            stmt = stmt.where(*conditions)
        return self.db.scalars(stmt).first()

    def get(self, entity: Optional[T] = None) -> List[T]:
        stmt = select(self.model)
        conditions = []
        if entity:
            for attr, value in vars(entity).items():
                if value is not None and hasattr(self.model, attr):
                    conditions.append(getattr(self.model, attr) == value)
        if hasattr(self.model, "deleted_at"):
            conditions.append(self.model.deleted_at.is_(None))
        if conditions:
            stmt = stmt.where(*conditions)
        return self.db.scalars(stmt).all()
