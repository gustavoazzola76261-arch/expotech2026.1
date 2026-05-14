from fastapi import APIRouter

from app.api.v1.controllers.iot_controller import (
    IoTController
)


router = APIRouter(
    tags=["IoT"]
)


@router.post("/sensor-data")
def receive_sensor_data():

    return IoTController.receive_sensor_data()