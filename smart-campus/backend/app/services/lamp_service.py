from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.repositories.lamp_repository import (
    LampRepository
)

from app.schemas.lamp_schema import (
    LampCreateSchema,
    LampUpdateSchema,
    LampResponseSchema
)


class LampService:

    @staticmethod
    def create_lamp(
        db: Session,
        lamp_data: LampCreateSchema
    ) -> LampResponseSchema:

        new_lamp = LampRepository.create_lamp(
            db=db,
            lamp_data={
                "name": lamp_data.name,
                "room_id": lamp_data.room_id,
                "status": lamp_data.status,
                "power_consumption": lamp_data.power_consumption
            }
        )

        return LampResponseSchema.model_validate(
            new_lamp
        )

    @staticmethod
    def get_all_lamps(
        db: Session
    ) -> list[LampResponseSchema]:

        lamps = LampRepository.get_all_lamps(db)

        return [
            LampResponseSchema.model_validate(lamp)
            for lamp in lamps
        ]

    @staticmethod
    def get_lamp_by_id(
        db: Session,
        lamp_id: int
    ) -> LampResponseSchema:

        lamp = LampRepository.get_lamp_by_id(
            db=db,
            lamp_id=lamp_id
        )

        if not lamp:
            raise HTTPException(
                status_code=404,
                detail="Lamp not found"
            )

        return LampResponseSchema.model_validate(
            lamp
        )

    @staticmethod
    def update_lamp(
        db: Session,
        lamp_id: int,
        lamp_data: LampUpdateSchema
    ) -> LampResponseSchema:

        lamp = LampRepository.get_lamp_by_id(
            db=db,
            lamp_id=lamp_id
        )

        if not lamp:
            raise HTTPException(
                status_code=404,
                detail="Lamp not found"
            )

        updated_lamp = LampRepository.update_lamp(
            db=db,
            lamp=lamp,
            update_data=lamp_data.model_dump(
                exclude_unset=True
            )
        )

        return LampResponseSchema.model_validate(
            updated_lamp
        )

    @staticmethod
    def delete_lamp(
        db: Session,
        lamp_id: int
    ) -> dict:

        lamp = LampRepository.get_lamp_by_id(
            db=db,
            lamp_id=lamp_id
        )

        if not lamp:
            raise HTTPException(
                status_code=404,
                detail="Lamp not found"
            )

        LampRepository.delete_lamp(
            db=db,
            lamp=lamp
        )

        return {
            "message": "Lamp deleted successfully"
        }

    @staticmethod
    def turn_on_lamp(
        db: Session,
        lamp_id: int
    ) -> LampResponseSchema:

        lamp = LampRepository.get_lamp_by_id(
            db=db,
            lamp_id=lamp_id
        )

        if not lamp:
            raise HTTPException(
                status_code=404,
                detail="Lamp not found"
            )

        updated_lamp = LampRepository.update_lamp(
            db=db,
            lamp=lamp,
            update_data={
                "status": True
            }
        )

        return LampResponseSchema.model_validate(
            updated_lamp
        )

    @staticmethod
    def turn_off_lamp(
        db: Session,
        lamp_id: int
    ) -> LampResponseSchema:

        lamp = LampRepository.get_lamp_by_id(
            db=db,
            lamp_id=lamp_id
        )

        if not lamp:
            raise HTTPException(
                status_code=404,
                detail="Lamp not found"
            )

        updated_lamp = LampRepository.update_lamp(
            db=db,
            lamp=lamp,
            update_data={
                "status": False
            }
        )

        return LampResponseSchema.model_validate(
            updated_lamp
        )