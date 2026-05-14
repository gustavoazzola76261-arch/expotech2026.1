from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import LampAction

if TYPE_CHECKING:
    from app.models.lamp import Lamp
    from app.models.user import User


class ActuationLog(Base):
    __tablename__ = "actuation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    lamp_id: Mapped[int] = mapped_column(ForeignKey("lamps.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[LampAction] = mapped_column(Enum(LampAction, name="lampaction"), nullable=False)
    energy_kwh: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)

    user: Mapped[User | None] = relationship("User", back_populates="actuation_logs")
    lamp: Mapped[Lamp] = relationship("Lamp", back_populates="actuation_logs")
