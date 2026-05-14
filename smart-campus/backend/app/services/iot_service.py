from sqlalchemy.orm import Session

from app.database.repositories.room_repository import (
    RoomRepository
)

from app.database.repositories.lamp_repository import (
    LampRepository
)

from app.database.repositories.device_repository import (
    DeviceRepository
)


class IoTService:

    @staticmethod
    def process_presence_sensor(
        db: Session,
        room_id: int,
        presence_detected: bool
    ):
        """
        Processa leitura do sensor PIR
        """

        room = RoomRepository.get_by_id(
            db=db,
            room_id=room_id
        )

        if not room:
            return None

        room.presence_detected = presence_detected

        if presence_detected:
            room.current_people = 1
        else:
            room.current_people = 0

        db.commit()
        db.refresh(room)

        return room

    @staticmethod
    def process_temperature_sensor(
        db: Session,
        device_id: int,
        temperature: float
    ):
        """
        Processa leitura de temperatura
        """

        device = DeviceRepository.get_by_id(
            db=db,
            device_id=device_id
        )

        if not device:
            return None

        device.last_temperature = temperature

        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def process_energy_sensor(
        db: Session,
        lamp_id: int,
        energy_consumption: float
    ):
        """
        Processa leitura energética
        """

        lamp = LampRepository.get_by_id(
            db=db,
            lamp_id=lamp_id
        )

        if not lamp:
            return None

        lamp.energy_consumption = energy_consumption

        db.commit()
        db.refresh(lamp)

        return lamp

    @staticmethod
    def process_lamp_status(
        db: Session,
        lamp_id: int,
        status: bool
    ):
        """
        Atualiza estado da lâmpada
        """

        lamp = LampRepository.get_by_id(
            db=db,
            lamp_id=lamp_id
        )

        if not lamp:
            return None

        lamp.is_on = status

        db.commit()
        db.refresh(lamp)

        return lamp