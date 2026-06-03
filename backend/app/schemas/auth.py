from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    room_ids: list[int] = Field(default_factory=list)
