from pydantic import BaseModel, Field

from app.models.air_conditioner import DEFAULT_AC_TEMP_C, MAX_AC_TEMP_C, MIN_AC_TEMP_C


class AirConditionerRead(BaseModel):
    id: int
    room_id: int
    name: str
    slot: int
    power_watts: int
    is_on: bool
    target_temp_c: int

    model_config = {"from_attributes": True}


class AirConditionerTemperatureUpdate(BaseModel):
    target_temp_c: int = Field(
        ge=MIN_AC_TEMP_C,
        le=MAX_AC_TEMP_C,
        description=f"Temperatura desejada ({MIN_AC_TEMP_C}–{MAX_AC_TEMP_C} °C)",
    )


class AirConditionerCommandBody(BaseModel):
    action: str = Field(pattern="^(on|off)$")


# Re-export defaults for API docs
AC_DEFAULT_TEMP_C = DEFAULT_AC_TEMP_C
