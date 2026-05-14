from app.services.lamp_service import (
    LampService
)


class LampsController:

    @staticmethod
    def turn_on(
        db,
        lamp_id: int
    ):

        return LampService.turn_on(
            db,
            lamp_id
        )

    @staticmethod
    def turn_off(
        db,
        lamp_id: int
    ):

        return LampService.turn_off(
            db,
            lamp_id
        )