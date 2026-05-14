from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.database.base import Base


class EnergyModel(Base):

    __tablename__ = "energy_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    room_id = Column(
        Integer,
        ForeignKey("rooms.id"),
        nullable=False
    )

    consumption_kwh = Column(
        Float,
        nullable=False
    )

    voltage = Column(
        Float,
        nullable=True
    )

    current = Column(
        Float,
        nullable=True
    )

    power = Column(
        Float,
        nullable=True
    )

    recorded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    room = relationship(
        "RoomModel",
        back_populates="energy_logs"
    )