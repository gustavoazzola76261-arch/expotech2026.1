from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.schemas.user_schema import (
    UserCreateSchema,
    UserResponseSchema
)

from app.api.v1.controllers.users_controller import (
    UsersController
)


router = APIRouter(
    tags=["Users"]
)


@router.post(
    "/",
    response_model=UserResponseSchema
)
def create_user(
    user_data: UserCreateSchema,
    db: Session = Depends(get_db)
):

    return UsersController.create_user(
        db,
        user_data
    )