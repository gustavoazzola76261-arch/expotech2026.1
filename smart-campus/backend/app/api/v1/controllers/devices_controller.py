from app.services.device_service import (
    DeviceService
)


class DevicesController:

    @staticmethod
    def get_devices(
        db
    ):

        return DeviceService.get_devices(
            db
        )

    @staticmethod
    def create_device(
        db,
        device_data
    ):

        return DeviceService.create_device(
            db,
            device_data.dict()
        )