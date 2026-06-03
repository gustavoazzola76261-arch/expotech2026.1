from pydantic import BaseModel, Field


class LampRead(BaseModel):
    id: int
    room_id: int
    name: str
    slot: int
    power_watts: int
    is_on: bool

    model_config = {"from_attributes": True}


class LampCommand(BaseModel):
    action: str = Field(pattern="^(on|off)$")
