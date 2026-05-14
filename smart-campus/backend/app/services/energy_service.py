from sqlalchemy.orm import Session

from app.database.repositories.energy_repository import (
    EnergyRepository
)

from app.schemas.energy_schema import (
    EnergyResponseSchema,
    EnergySummaryResponseSchema
)


class EnergyService:

    @staticmethod
    def get_energy_logs(
        db: Session
    ) -> list[EnergyResponseSchema]:

        logs = EnergyRepository.get_all_logs(db)

        return [
            EnergyResponseSchema.model_validate(log)
            for log in logs
        ]

    @staticmethod
    def get_total_consumption(
        db: Session
    ) -> EnergySummaryResponseSchema:

        total_consumption = (
            EnergyRepository.calculate_total_consumption(db)
        )

        total_active_devices = (
            EnergyRepository.count_active_devices(db)
        )

        return EnergySummaryResponseSchema(
            total_consumption=total_consumption,
            active_devices=total_active_devices
        )

    @staticmethod
    def get_room_consumption(
        db: Session,
        room_id: int
    ) -> dict:

        consumption = (
            EnergyRepository.calculate_room_consumption(
                db=db,
                room_id=room_id
            )
        )

        return {
            "room_id": room_id,
            "consumption": consumption
        }