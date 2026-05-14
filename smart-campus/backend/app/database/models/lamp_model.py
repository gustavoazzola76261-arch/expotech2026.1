from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.database.base import Base


class LampModel(Base):

    __tablename__ = "lamps"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    room_id = Column(
        Integer,
        ForeignKey("rooms.id"),
        nullable=False
    )

    is_on = Column(
        Boolean,
        default=False
    )

    power_watts = Column(
        Float,
        default=0.0
    )

    energy_consumption = Column(
        Float,
        default=0.0
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    room = relationship(
        "RoomModel",
        back_populates="lamps"
    )