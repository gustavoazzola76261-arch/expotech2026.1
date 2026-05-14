from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.repositories.user_repository import (
    UserRepository
)

from app.schemas.user_schema import (
    UserCreateSchema,
    UserUpdateSchema,
    UserResponseSchema
)

from app.core.security.password_handler import (
    hash_password
)


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        user_data: UserCreateSchema
    ) -> UserResponseSchema:

        existing_user = UserRepository.get_user_by_email(
            db=db,
            email=user_data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        hashed_password = hash_password(
            user_data.password
        )

        new_user = UserRepository.create_user(
            db=db,
            user_data={
                "name": user_data.name,
                "email": user_data.email,
                "password": hashed_password,
                "role": user_data.role
            }
        )

        return UserResponseSchema.model_validate(new_user)

    @staticmethod
    def get_all_users(
        db: Session
    ) -> list[UserResponseSchema]:

        users = UserRepository.get_all_users(db)

        return [
            UserResponseSchema.model_validate(user)
            for user in users
        ]

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int
    ) -> UserResponseSchema:

        user = UserRepository.get_user_by_id(
            db=db,
            user_id=user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return UserResponseSchema.model_validate(user)

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        user_data: UserUpdateSchema
    ) -> UserResponseSchema:

        user = UserRepository.get_user_by_id(
            db=db,
            user_id=user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        updated_user = UserRepository.update_user(
            db=db,
            user=user,
            update_data=user_data.model_dump(
                exclude_unset=True
            )
        )

        return UserResponseSchema.model_validate(
            updated_user
        )

    @staticmethod
    def delete_user(
        db: Session,
        user_id: int
    ) -> dict:

        user = UserRepository.get_user_by_id(
            db=db,
            user_id=user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        UserRepository.delete_user(
            db=db,
            user=user
        )

        return {
            "message": "User deleted successfully"
        }