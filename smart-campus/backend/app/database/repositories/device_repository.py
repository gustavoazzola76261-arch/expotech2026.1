from sqlalchemy.orm import Session

from app.database.models.device_model import (
    DeviceModel
)


class DeviceRepository:

    @staticmethod
    def create(
        db: Session,
        device_data: dict
    ):
        """
        Cria um novo dispositivo
        """

        device = DeviceModel(**device_data)

        db.add(device)
        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def get_by_id(
        db: Session,
        device_id: int
    ):
        """
        Busca dispositivo por ID
        """

        return db.query(DeviceModel).filter(
            DeviceModel.id == device_id
        ).first()

    @staticmethod
    def get_all(
        db: Session
    ):
        """
        Lista todos os dispositivos
        """

        return db.query(DeviceModel).all()

    @staticmethod
    def get_by_room(
        db: Session,
        room_id: int
    ):
        """
        Lista dispositivos por sala
        """

        return db.query(DeviceModel).filter(
            DeviceModel.room_id == room_id
        ).all()

    @staticmethod
    def update(
        db: Session,
        device: DeviceModel,
        update_data: dict
    ):
        """
        Atualiza dispositivo
        """

        for key, value in update_data.items():
            setattr(device, key, value)

        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def update_temperature(
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
    def update_status(
        db: Session,
        device: DeviceModel,
        status: bool
    ):
        """
        Atualiza status do dispositivo
        """

        device.is_active = status

        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def delete(
        db: Session,
        device: DeviceModel
    ):
        """
        Remove dispositivo
        """

        db.delete(device)
        db.commit()

        return True