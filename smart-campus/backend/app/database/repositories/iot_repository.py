from sqlalchemy.orm import Session

from app.database.models.device_model import (
    DeviceModel
)

from app.database.models.room_model import (
    RoomModel
)

from app.database.models.lamp_model import (
    LampModel
)


class IoTRepository:

    @staticmethod
    def get_device_by_id(
        db: Session,
        device_id: int
    ):
        """
        Busca dispositivo IoT por ID
        """

        return db.query(DeviceModel).filter(
            DeviceModel.id == device_id
        ).first()

    @staticmethod
    def get_room_by_id(
        db: Session,
        room_id: int
    ):
        """
        Busca sala por ID
        """

        return db.query(RoomModel).filter(
            RoomModel.id == room_id
        ).first()

    @staticmethod
    def get_lamp_by_id(
        db: Session,
        lamp_id: int
    ):
        """
        Busca lâmpada por ID
        """

        return db.query(LampModel).filter(
            LampModel.id == lamp_id
        ).first()

    @staticmethod
    def update_room_presence(
        db: Session,
        room: RoomModel,
        presence_detected: bool,
        current_people: int
    ):
        """
        Atualiza presença da sala
        """

        room.presence_detected = presence_detected
        room.current_people = current_people

        db.commit()
        db.refresh(room)

        return room

    @staticmethod
    def update_device_temperature(
        db: Session,
        device: DeviceModel,
        temperature: float
    ):
        """
        Atualiza temperatura do dispositivo
        """

        device.last_temperature = temperature

        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def update_lamp_status(
        db: Session,
        lamp: LampModel,
        status: bool
    ):
        """
        Atualiza estado da lâmpada
        """

        lamp.is_on = status

        db.commit()
        db.refresh(lamp)

        return lamp

    @staticmethod
    def update_lamp_energy(
        db: Session,
        lamp: LampModel,
        energy_consumption: float
    ):
        """
        Atualiza consumo energético da lâmpada
        """

        lamp.energy_consumption = energy_consumption

        db.commit()
        db.refresh(lamp)

        return lamp