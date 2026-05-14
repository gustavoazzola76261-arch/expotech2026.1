from app.services.user_service import (
    UserService
)


class UsersController:

    @staticmethod
    def create_user(
        db,
        user_data
    ):

        return UserService.create_user(
            db,
            user_data.dict()
        )