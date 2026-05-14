from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.schemas.auth_schema import (
    LoginSchema
)

from app.api.v1.controllers.auth_controller import (
    AuthController
)


router = APIRouter(
    tags=["Authentication"]
)


@router.post("/login")
def login(
    login_data: LoginSchema,
    db: Session = Depends(get_db)
):

    return AuthController.login(
        db,
        login_data
    )


@router.post("/refresh")
def refresh_token():

    return {
        "message": (
            "Refresh token "
            "not implemented yet"
        )
    }