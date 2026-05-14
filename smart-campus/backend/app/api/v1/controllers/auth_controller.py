from app.services.auth_service import (
    AuthService
)


class AuthController:

    @staticmethod
    def login(
        db,
        login_data
    ):

        return AuthService.login(
            db=db,
            email=login_data.email,
            password=login_data.password
        )