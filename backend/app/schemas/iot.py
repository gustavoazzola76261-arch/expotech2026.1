from pydantic import BaseModel


class IoTLampState(BaseModel):
    lamp_id: int
    room_id: int
    room_code: str
    room_name: str
    slot: int
    name: str
    is_on: bool


class IoTStateResponse(BaseModel):
    lamps: list[IoTLampState]
    poll_interval_ms: int = 2000
