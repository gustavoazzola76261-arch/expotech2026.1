from sqlalchemy.orm import Session

from app.database.models.lamp_model import (
    LampModel
)


class LampRepository:

    @staticmethod
    def create(
        db: Session,
        lamp_data: dict
    ):
        """
        Cria uma nova lâmpada
        """

        lamp = LampModel(**lamp_data)

        db.add(lamp)
        db.commit()
        db.refresh(lamp)

        return lamp

    @staticmethod
    def get_by_id(
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
    def get_all(
        db: Session
    ):
        """
        Lista todas as lâmpadas
        """

        return db.query(LampModel).all()

    @staticmethod
    def get_by_room(
        db: Session,
        room_id: int
    ):
        """
        Lista lâmpadas de uma sala
        """

        return db.query(LampModel).filter(
            LampModel.room_id == room_id
        ).all()

    @staticmethod
    def update(
        db: Session,
        lamp: LampModel,
        update_data: dict
    ):
        """
        Atualiza dados da lâmpada
        """

        for key, value in update_data.items():
            setattr(lamp, key, value)

        db.commit()
        db.refresh(lamp)

        return lamp

    @staticmethod
    def update_status(
        db: Session,
        lamp: LampModel,
        status: bool
    ):
        """
        Liga ou desliga lâmpada
        """

        lamp.is_on = status

        db.commit()
        db.refresh(lamp)

        return lamp

    @staticmethod
    def update_energy_consumption(
        db: Session,
        lamp: LampModel,
        energy_consumption: float
    ):
        """
        Atualiza consumo energético
        """

        lamp.energy_consumption = energy_consumption

        db.commit()
        db.refresh(lamp)

        return lamp

    @staticmethod
    def delete(
        db: Session,
        lamp: LampModel
    ):
        """
        Remove lâmpada
        """

        db.delete(lamp)
        db.commit()

        return True