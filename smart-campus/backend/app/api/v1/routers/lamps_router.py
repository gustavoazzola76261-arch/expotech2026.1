from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.schemas.lamp_schema import (
    LampResponseSchema
)

from app.api.v1.controllers.lamps_controller import (
    LampsController
)


router = APIRouter(
    tags=["Lamps"]
)


@router.post(
    "/{lamp_id}/on",
    response_model=LampResponseSchema
)
def turn_on_lamp(
    lamp_id: int,
    db: Session = Depends(get_db)
):

    return LampsController.turn_on(
        db,
        lamp_id
    )


@router.post(
    "/{lamp_id}/off",
    response_model=LampResponseSchema
)
def turn_off_lamp(
    lamp_id: int,
    db: Session = Depends(get_db)
):

    return LampsController.turn_off(
        db,
        lamp_id
    )