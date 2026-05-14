from fastapi import APIRouter

from app.api.v1.controllers.energy_controller import (
    EnergyController
)


router = APIRouter(
    tags=["Energy"]
)


@router.get("/")
def get_consumption():

    return EnergyController.get_consumption()