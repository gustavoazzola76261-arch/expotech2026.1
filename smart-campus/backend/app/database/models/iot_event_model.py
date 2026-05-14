from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class IoTEventModel(Base):
    __tablename__ = "iot_events"

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

    device_id = Column(
        Integer,
        ForeignKey("devices.id"),
        nullable=True
    )

    event_type = Column(
        String,
        nullable=False
    )

    sensor_name = Column(
        String,
        nullable=True
    )

    sensor_value = Column(
        String,
        nullable=True
    )

    processed = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    room = relationship(
        "RoomModel",
        back_populates="iot_events"
    )

    device = relationship(
        "DeviceModel",
        back_populates="iot_events"
    )