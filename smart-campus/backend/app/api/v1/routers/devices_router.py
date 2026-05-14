from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.schemas.device_schema import (
    DeviceCreateSchema,
    DeviceResponseSchema
)

from app.api.v1.controllers.devices_controller import (
    DevicesController
)


router = APIRouter(
    tags=["Devices"]
)


@router.get(
    "/",
    response_model=list[DeviceResponseSchema]
)
def get_devices(
    db: Session = Depends(get_db)
):

    return DevicesController.get_devices(
        db
    )


@router.post(
    "/",
    response_model=DeviceResponseSchema
)
def create_device(
    device_data: DeviceCreateSchema,
    db: Session = Depends(get_db)
):

    return DevicesController.create_device(
        db,
        device_data
    )