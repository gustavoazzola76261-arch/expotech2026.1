from pydantic import BaseModel
from datetime import datetime


class DeviceBaseSchema(BaseModel):
    name: str
    type: str
    status: bool
    room_id: int


class DeviceCreateSchema(DeviceBaseSchema):
    pass


class DeviceUpdateSchema(BaseModel):
    name: str | None = None
    type: str | None = None
    status: bool | None = None
    room_id: int | None = None


class DeviceResponseSchema(DeviceBaseSchema):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True