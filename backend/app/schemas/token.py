from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    email: str
    role: str
    full_name: str
    user: Optional[dict] = None


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
