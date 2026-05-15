from pydantic import BaseModel, Field

from app.schemas.lamp import LampRead


class RoomBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=64)


class RoomCreate(RoomBase):
    id: int | None = Field(None, gt=0, description="ID desejado (opcional). Deve estar livre no banco.")


class RoomUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    code: str | None = Field(None, min_length=1, max_length=64)
    new_id: int | None = Field(None, gt=0, description="Novo ID numérico da sala (deve estar livre)")


class RoomRead(RoomBase):
    id: int

    model_config = {"from_attributes": True}


class RoomOverview(RoomRead):
    lamps: list[LampRead] = Field(default_factory=list)
