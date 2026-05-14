from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.room import Room
    from app.models.user import User


class UserRoom(Base):
    """Links professors to rooms they may control."""

    __tablename__ = "user_rooms"
    __table_args__ = (UniqueConstraint("user_id", "room_id", name="uq_user_room"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="room_assignments")
    room: Mapped[Room] = relationship("Room", back_populates="user_assignments")
