from pydantic import BaseModel
from datetime import datetime


class LampBaseSchema(BaseModel):
    name: str
    status: bool
    room_id: int


class LampCreateSchema(LampBaseSchema):
    pass


class LampUpdateSchema(BaseModel):
    name: str | None = None
    status: bool | None = None
    room_id: int | None = None


class LampResponseSchema(LampBaseSchema):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True