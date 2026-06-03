from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import LampAction, ScheduleScope

if TYPE_CHECKING:
    from app.models.lamp import Lamp
    from app.models.room import Room
    from app.models.user import User


class LampSchedule(Base):
    __tablename__ = "lamp_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[ScheduleScope] = mapped_column(Enum(ScheduleScope, name="schedulescope"), nullable=False)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=True)
    lamp_id: Mapped[int | None] = mapped_column(ForeignKey("lamps.id", ondelete="CASCADE"), nullable=True)
    room_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    lamp_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    action: Mapped[LampAction] = mapped_column(Enum(LampAction, name="lampaction", create_type=False), nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    # 0=segunda … 6=domingo (ISO weekday). None ou vazio = todos os dias.
    days_of_week: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    room: Mapped[Room | None] = relationship("Room")
    lamp: Mapped[Lamp | None] = relationship("Lamp")
    created_by: Mapped[User | None] = relationship("User")
