from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.database.base import Base


class RoomModel(Base):

    __tablename__ = "rooms"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False,
        unique=True
    )

    description = Column(
        String,
        nullable=True
    )

    floor = Column(
        Integer,
        nullable=False
    )

    capacity = Column(
        Integer,
        default=0
    )

    current_people = Column(
        Integer,
        default=0
    )

    presence_detected = Column(
        Boolean,
        default=False
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

    lamps = relationship(
        "LampModel",
        back_populates="room"
    )

    devices = relationship(
        "DeviceModel",
        back_populates="room"
    )

    energy_records = relationship(
        "EnergyModel",
        back_populates="room"
    )
    energy_logs = relationship(
    "EnergyLogModel",
    back_populates="room"
)

iot_events = relationship(
    "IoTEventModel",
    back_populates="room"
)