from pydantic import BaseModel, Field, field_validator

from app.schemas.ac import AirConditionerRead
from app.schemas.lamp import LampRead

MAX_LAMPS_PER_ROOM = 12
MAX_AC_UNITS_PER_ROOM = 4


class LampConfigInput(BaseModel):
    power_watts: int = Field(ge=1, le=5000)


class AcConfigInput(BaseModel):
    power_watts: int = Field(ge=1, le=20000)


class RoomBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=64)


class RoomCreate(RoomBase):
    id: int | None = Field(None, gt=0, description="ID desejado (opcional). Deve estar livre no banco.")
    lamp_count: int = Field(default=3, ge=1, le=MAX_LAMPS_PER_ROOM)
    default_power_watts: int = Field(default=20, ge=1, le=5000)
    ac_count: int = Field(default=1, ge=0, le=MAX_AC_UNITS_PER_ROOM)
    default_ac_power_watts: int = Field(default=1500, ge=1, le=20000)


class RoomUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    code: str | None = Field(None, min_length=1, max_length=64)
    lamps: list[LampConfigInput] | None = Field(
        None,
        min_length=1,
        max_length=MAX_LAMPS_PER_ROOM,
        description="Lista de lâmpadas (quantidade = len(lamps)); ordem define o slot",
    )
    air_conditioners: list[AcConfigInput] | None = Field(
        None,
        min_length=0,
        max_length=MAX_AC_UNITS_PER_ROOM,
        description="Lista de aparelhos de ar (quantidade = len); ordem define o slot",
    )

    @field_validator("lamps")
    @classmethod
    def lamps_not_empty(cls, v: list[LampConfigInput] | None) -> list[LampConfigInput] | None:
        if v is not None and len(v) == 0:
            raise ValueError("Informe ao menos uma lâmpada")
        return v


class RoomRead(RoomBase):
    id: int

    model_config = {"from_attributes": True}


class RoomOverview(RoomRead):
    lamps: list[LampRead] = Field(default_factory=list)
    air_conditioners: list[AirConditionerRead] = Field(default_factory=list)
