from pydantic import BaseModel
from datetime import datetime


class BlacklistJtiDto(BaseModel):
    jti: str
    account_id: int
    expires_at: datetime
