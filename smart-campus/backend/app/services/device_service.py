from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.repositories.device_repository import (
    DeviceRepository
)

from app.schemas.device_schema import (
    DeviceCreateSchema,
    DeviceUpdateSchema,
    DeviceResponseSchema
)


class DeviceService:

    @staticmethod
    def create_device(
        db: Session,
        device_data: DeviceCreateSchema
    ) -> DeviceResponseSchema:

        new_device = DeviceRepository.create_device(
            db=db,
            device_data={
                "name": device_data.name,
                "device_type": device_data.device_type,
                "room_id": device_data.room_id,
                "status": device_data.status
            }
        )

        return DeviceResponseSchema.model_validate(
            new_device
        )

    @staticmethod
    def get_all_devices(
        db: Session
    ) -> list[DeviceResponseSchema]:

        devices = DeviceRepository.get_all_devices(db)

        return [
            DeviceResponseSchema.model_validate(device)
            for device in devices
        ]

    @staticmethod
    def get_device_by_id(
        db: Session,
        device_id: int
    ) -> DeviceResponseSchema:

        device = DeviceRepository.get_device_by_id(
            db=db,
            device_id=device_id
        )

        if not device:
            raise HTTPException(
                status_code=404,
                detail="Device not found"
            )

        return DeviceResponseSchema.model_validate(
            device
        )

    @staticmethod
    def update_device(
        db: Session,
        device_id: int,
        device_data: DeviceUpdateSchema
    ) -> DeviceResponseSchema:

        device = DeviceRepository.get_device_by_id(
            db=db,
            device_id=device_id
        )

        if not device:
            raise HTTPException(
                status_code=404,
                detail="Device not found"
            )

        updated_device = DeviceRepository.update_device(
            db=db,
            device=device,
            update_data=device_data.model_dump(
                exclude_unset=True
            )
        )

        return DeviceResponseSchema.model_validate(
            updated_device
        )

    @staticmethod
    def delete_device(
        db: Session,
        device_id: int
    ) -> dict:

        device = DeviceRepository.get_device_by_id(
            db=db,
            device_id=device_id
        )

        if not device:
            raise HTTPException(
                status_code=404,
                detail="Device not found"
            )

        DeviceRepository.delete_device(
            db=db,
            device=device
        )

        return {
            "message": "Device deleted successfully"
        }

    @staticmethod
    def activate_device(
        db: Session,
        device_id: int
    ) -> DeviceResponseSchema:

        device = DeviceRepository.get_device_by_id(
            db=db,
            device_id=device_id
        )

        if not device:
            raise HTTPException(
                status_code=404,
                detail="Device not found"
            )

        updated_device = DeviceRepository.update_device(
            db=db,
            device=device,
            update_data={
                "status": True
            }
        )

        return DeviceResponseSchema.model_validate(
            updated_device
        )

    @staticmethod
    def deactivate_device(
        db: Session,
        device_id: int
    ) -> DeviceResponseSchema:

        device = DeviceRepository.get_device_by_id(
            db=db,
            device_id=device_id
        )

        if not device:
            raise HTTPException(
                status_code=404,
                detail="Device not found"
            )

        updated_device = DeviceRepository.update_device(
            db=db,
            device=device,
            update_data={
                "status": False
            }
        )

        return DeviceResponseSchema.model_validate(
            updated_device
        )