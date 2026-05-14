from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr
    role: str


class UserCreateSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserResponseSchema(UserBaseSchema):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True