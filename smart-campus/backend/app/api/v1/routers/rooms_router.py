from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.schemas.room_schema import (
    RoomCreateSchema,
    RoomResponseSchema
)

from app.api.v1.controllers.rooms_controller import (
    RoomsController
)


router = APIRouter(
    tags=["Rooms"]
)


@router.get(
    "/",
    response_model=list[RoomResponseSchema]
)
def get_rooms(
    db: Session = Depends(get_db)
):

    return RoomsController.get_rooms(
        db
    )


@router.post(
    "/",
    response_model=RoomResponseSchema
)
def create_room(
    room_data: RoomCreateSchema,
    db: Session = Depends(get_db)
):

    return RoomsController.create_room(
        db,
        room_data
    )