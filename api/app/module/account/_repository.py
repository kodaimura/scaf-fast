from sqlalchemy.orm import Session
from app.core.repository import BaseRepository
from .model import Account


class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: Session):
        super().__init__(db, Account)
