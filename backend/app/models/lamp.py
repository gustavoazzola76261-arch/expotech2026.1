from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.actuation_log import ActuationLog
    from app.models.room import Room


class Lamp(Base):
    __tablename__ = "lamps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slot: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    power_watts: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    is_on: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_on_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    room: Mapped[Room] = relationship("Room", back_populates="lamps")
    actuation_logs: Mapped[list[ActuationLog]] = relationship(
        "ActuationLog",
        back_populates="lamp",
        passive_deletes=True,
    )
