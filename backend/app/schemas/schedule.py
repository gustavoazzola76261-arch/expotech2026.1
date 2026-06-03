from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.enums import LampAction, ScheduleScope

WEEKDAY_LABELS = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")


def normalize_days_of_week(days: list[int] | None) -> list[int] | None:
    if days is None or len(days) == 0:
        return None
    unique = sorted(set(days))
    for d in unique:
        if d < 0 or d > 6:
            raise ValueError("days_of_week deve usar 0=segunda … 6=domingo")
    return unique


class ScheduleBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    scope: ScheduleScope
    action: LampAction
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    room_id: int | None = None
    lamp_id: int | None = None
    room_ids: list[int] | None = None
    lamp_ids: list[int] | None = None
    days_of_week: list[int] | None = Field(
        default=None,
        description="0=segunda … 6=domingo; vazio = todos os dias",
    )
    is_enabled: bool = True

    @field_validator("days_of_week", mode="before")
    @classmethod
    def coerce_days(cls, v: object) -> list[int] | None:
        if v is None:
            return None
        if isinstance(v, list) and len(v) == 0:
            return None
        return v  # type: ignore[return-value]

    @model_validator(mode="after")
    def validate_scope_targets(self) -> "ScheduleBase":
        self.days_of_week = normalize_days_of_week(self.days_of_week)
        if self.scope == ScheduleScope.room:
            if self.room_id is None:
                raise ValueError("room_id é obrigatório quando scope=room")
            self.lamp_id = None
            self.room_ids = None
            self.lamp_ids = None
        elif self.scope == ScheduleScope.rooms_group:
            if not self.room_ids:
                raise ValueError("room_ids deve conter ao menos uma sala quando scope=rooms_group")
            self.room_id = None
            self.lamp_id = None
            self.lamp_ids = None
            self.room_ids = sorted(set(self.room_ids))
        elif self.scope == ScheduleScope.lamp:
            if self.lamp_id is None:
                raise ValueError("lamp_id é obrigatório quando scope=lamp")
            self.room_id = None
            self.room_ids = None
            self.lamp_ids = None
        elif self.scope == ScheduleScope.lamps_group:
            if not self.lamp_ids:
                raise ValueError("lamp_ids deve conter ao menos uma lâmpada quando scope=lamps_group")
            self.room_id = None
            self.lamp_id = None
            self.room_ids = None
            self.lamp_ids = sorted(set(self.lamp_ids))
        elif self.scope == ScheduleScope.all:
            self.room_id = None
            self.lamp_id = None
            self.room_ids = None
            self.lamp_ids = None
        return self


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    scope: ScheduleScope | None = None
    action: LampAction | None = None
    hour: int | None = Field(None, ge=0, le=23)
    minute: int | None = Field(None, ge=0, le=59)
    room_id: int | None = None
    lamp_id: int | None = None
    room_ids: list[int] | None = None
    lamp_ids: list[int] | None = None
    days_of_week: list[int] | None = None
    is_enabled: bool | None = None

    @field_validator("days_of_week", mode="before")
    @classmethod
    def coerce_days(cls, v: object) -> list[int] | None:
        if v is None:
            return None
        if isinstance(v, list) and len(v) == 0:
            return None
        return v  # type: ignore[return-value]


class ScheduleRead(BaseModel):
    id: int
    name: str
    scope: ScheduleScope
    action: LampAction
    hour: int
    minute: int
    room_id: int | None
    lamp_id: int | None
    room_ids: list[int] | None = None
    lamp_ids: list[int] | None = None
    days_of_week: list[int] | None = None
    days_label: str | None = None
    is_enabled: bool
    room_name: str | None = None
    lamp_name: str | None = None
    target_label: str | None = None

    model_config = {"from_attributes": True}
