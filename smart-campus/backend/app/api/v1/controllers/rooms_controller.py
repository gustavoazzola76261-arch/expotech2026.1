from app.services.room_service import (
    RoomService
)


class RoomsController:

    @staticmethod
    def get_rooms(
        db
    ):

        return RoomService.get_rooms(
            db
        )

    @staticmethod
    def create_room(
        db,
        room_data
    ):

        return RoomService.create_room(
            db,
            room_data.dict()
        )