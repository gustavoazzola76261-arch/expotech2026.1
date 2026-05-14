from pydantic import BaseModel
from datetime import datetime


class RoomBaseSchema(BaseModel):
    name: str
    block: str
    floor: int


class RoomCreateSchema(RoomBaseSchema):
    pass


class RoomUpdateSchema(BaseModel):
    name: str | None = None
    block: str | None = None
    floor: int | None = None


class RoomResponseSchema(RoomBaseSchema):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True