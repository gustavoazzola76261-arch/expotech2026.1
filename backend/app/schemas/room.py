from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=64)


class RoomRead(RoomBase):
    id: int

    model_config = {"from_attributes": True}
