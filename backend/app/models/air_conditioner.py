from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ac_actuation_log import AcActuationLog
    from app.models.room import Room

DEFAULT_AC_TEMP_C = 23
MIN_AC_TEMP_C = 16
MAX_AC_TEMP_C = 30
DEFAULT_AC_POWER_W = 1500
MAX_AC_UNITS_PER_ROOM = 4


class AirConditioner(Base):
    __tablename__ = "room_air_conditioners"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slot: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    power_watts: Mapped[int] = mapped_column(Integer, nullable=False, default=DEFAULT_AC_POWER_W)
    is_on: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_on_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    target_temp_c: Mapped[int] = mapped_column(Integer, default=DEFAULT_AC_TEMP_C, nullable=False)

    room: Mapped[Room] = relationship("Room", back_populates="air_conditioners")
    actuation_logs: Mapped[list[AcActuationLog]] = relationship(
        "AcActuationLog",
        back_populates="air_conditioner",
        passive_deletes=True,
    )
