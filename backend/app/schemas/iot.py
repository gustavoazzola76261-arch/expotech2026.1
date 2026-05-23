from pydantic import BaseModel


class IoTLampState(BaseModel):
    lamp_id: int
    room_id: int
    room_code: str
    room_name: str
    slot: int
    name: str
    is_on: bool


class IoTAcState(BaseModel):
    room_id: int
    room_code: str
    is_on: bool
    target_temp_c: int


class IoTStateResponse(BaseModel):
    lamps: list[IoTLampState]
    air_conditioners: list[IoTAcState] = []
    poll_interval_ms: int = 2000
