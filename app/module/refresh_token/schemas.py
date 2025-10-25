from pydantic import BaseModel
from datetime import datetime


class RefreshTokenResponse(BaseModel):
    id: int
    account_id: int
    issued_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None

    class Config:
        orm_mode = True
