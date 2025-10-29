from datetime import datetime
from pydantic import BaseModel


class BlacklistAddDto(BaseModel):
    jti: str
    expires_at: datetime
