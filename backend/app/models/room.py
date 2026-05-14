from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.lamp import Lamp
    from app.models.user_room import UserRoom


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (UniqueConstraint("code", name="uq_rooms_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    lamps: Mapped[list[Lamp]] = relationship(
        "Lamp", back_populates="room", cascade="all, delete-orphan"
    )
    user_assignments: Mapped[list[UserRoom]] = relationship(
        "UserRoom", back_populates="room", cascade="all, delete-orphan"
    )
