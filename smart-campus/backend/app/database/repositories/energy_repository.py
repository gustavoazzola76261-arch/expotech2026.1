from sqlalchemy.orm import Session

from app.database.models.energy_model import (
    EnergyModel
)


class EnergyRepository:

    @staticmethod
    def create(
        db: Session,
        energy_data: dict
    ):
        """
        Cria um registro energético
        """

        energy = EnergyModel(**energy_data)

        db.add(energy)
        db.commit()
        db.refresh(energy)

        return energy

    @staticmethod
    def get_by_id(
        db: Session,
        energy_id: int
    ):
        """
        Busca registro energético por ID
        """

        return db.query(EnergyModel).filter(
            EnergyModel.id == energy_id
        ).first()

    @staticmethod
    def get_all(
        db: Session
    ):
        """
        Lista todos os registros energéticos
        """

        return db.query(EnergyModel).all()

    @staticmethod
    def get_by_room(
        db: Session,
        room_id: int
    ):
        """
        Lista registros energéticos por sala
        """

        return db.query(EnergyModel).filter(
            EnergyModel.room_id == room_id
        ).all()

    @staticmethod
    def update(
        db: Session,
        energy: EnergyModel,
        update_data: dict
    ):
        """
        Atualiza registro energético
        """

        for key, value in update_data.items():
            setattr(energy, key, value)

        db.commit()
        db.refresh(energy)

        return energy

    @staticmethod
    def delete(
        db: Session,
        energy: EnergyModel
    ):
        """
        Remove registro energético
        """

        db.delete(energy)
        db.commit()

        return True