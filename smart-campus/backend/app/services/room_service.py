from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.repositories.room_repository import (
    RoomRepository
)

from app.schemas.room_schema import (
    RoomCreateSchema,
    RoomUpdateSchema,
    RoomResponseSchema
)


class RoomService:

    @staticmethod
    def create_room(
        db: Session,
        room_data: RoomCreateSchema
    ) -> RoomResponseSchema:

        existing_room = RoomRepository.get_room_by_name(
            db=db,
            name=room_data.name
        )

        if existing_room:
            raise HTTPException(
                status_code=400,
                detail="Room already exists"
            )

        new_room = RoomRepository.create_room(
            db=db,
            room_data={
                "name": room_data.name,
                "floor": room_data.floor,
                "description": room_data.description
            }
        )

        return RoomResponseSchema.model_validate(
            new_room
        )

    @staticmethod
    def get_all_rooms(
        db: Session
    ) -> list[RoomResponseSchema]:

        rooms = RoomRepository.get_all_rooms(db)

        return [
            RoomResponseSchema.model_validate(room)
            for room in rooms
        ]

    @staticmethod
    def get_room_by_id(
        db: Session,
        room_id: int
    ) -> RoomResponseSchema:

        room = RoomRepository.get_room_by_id(
            db=db,
            room_id=room_id
        )

        if not room:
            raise HTTPException(
                status_code=404,
                detail="Room not found"
            )

        return RoomResponseSchema.model_validate(room)

    @staticmethod
    def update_room(
        db: Session,
        room_id: int,
        room_data: RoomUpdateSchema
    ) -> RoomResponseSchema:

        room = RoomRepository.get_room_by_id(
            db=db,
            room_id=room_id
        )

        if not room:
            raise HTTPException(
                status_code=404,
                detail="Room not found"
            )

        updated_room = RoomRepository.update_room(
            db=db,
            room=room,
            update_data=room_data.model_dump(
                exclude_unset=True
            )
        )

        return RoomResponseSchema.model_validate(
            updated_room
        )

    @staticmethod
    def delete_room(
        db: Session,
        room_id: int
    ) -> dict:

        room = RoomRepository.get_room_by_id(
            db=db,
            room_id=room_id
        )

        if not room:
            raise HTTPException(
                status_code=404,
                detail="Room not found"
            )

        RoomRepository.delete_room(
            db=db,
            room=room
        )

        return {
            "message": "Room deleted successfully"
        }