from pydantic import BaseModel
from datetime import datetime


class IoTEventBaseSchema(BaseModel):
    device_id: int
    event_type: str
    value: str


class IoTEventCreateSchema(IoTEventBaseSchema):
    pass


class IoTEventResponseSchema(IoTEventBaseSchema):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True