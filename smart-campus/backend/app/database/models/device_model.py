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


class DeviceModel(Base):

    __tablename__ = "devices"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    device_type = Column(
        String,
        nullable=False
    )

    room_id = Column(
        Integer,
        ForeignKey("rooms.id"),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    ip_address = Column(
        String,
        nullable=True
    )

    mac_address = Column(
        String,
        nullable=True
    )

    firmware_version = Column(
        String,
        nullable=True
    )

    last_temperature = Column(
        Float,
        nullable=True
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
        back_populates="devices"
    )
    energy_logs = relationship(
    "EnergyLogModel",
    back_populates="device"
)

iot_events = relationship(
    "IoTEventModel",
    back_populates="device"
)