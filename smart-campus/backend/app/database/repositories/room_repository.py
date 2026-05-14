from sqlalchemy.orm import Session

from app.database.models.room_model import (
    RoomModel
)


class RoomRepository:

    @staticmethod
    def create(
        db: Session,
        room_data: dict
    ):
        """
        Cria uma nova sala
        """

        room = RoomModel(**room_data)

        db.add(room)
        db.commit()
        db.refresh(room)

        return room

    @staticmethod
    def get_by_id(
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
    def get_by_name(
        db: Session,
        room_name: str
    ):
        """
        Busca sala pelo nome
        """

        return db.query(RoomModel).filter(
            RoomModel.name == room_name
        ).first()

    @staticmethod
    def get_all(
        db: Session
    ):
        """
        Lista todas as salas
        """

        return db.query(RoomModel).all()

    @staticmethod
    def update(
        db: Session,
        room: RoomModel,
        update_data: dict
    ):
        """
        Atualiza sala
        """

        for key, value in update_data.items():
            setattr(room, key, value)

        db.commit()
        db.refresh(room)

        return room

    @staticmethod
    def update_presence(
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
    def delete(
        db: Session,
        room: RoomModel
    ):
        """
        Remove sala
        """

        db.delete(room)
        db.commit()

        return True