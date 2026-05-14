from pydantic import BaseModel
from datetime import datetime


class EnergyLogBaseSchema(BaseModel):
    room_id: int
    consumption_kwh: float


class EnergyLogCreateSchema(EnergyLogBaseSchema):
    pass


class EnergyLogResponseSchema(EnergyLogBaseSchema):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True