from pydantic import BaseModel
from typing import Optional


class LoginSchema(BaseModel):
    email: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    email: Optional[str] = None