from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token
)

from app.core.security.password_handler import (verify_password)
from app.database.repositories.user_repository import (UserRepository)
from app.schemas.auth_schema import (
    LoginSchema,
    TokenSchema
)

from app.schemas.user_schema import (
    UserResponseSchema
)

from app.core.config.settings import settings


class AuthService:

    @staticmethod
    def login(
        db: Session,
        credentials: LoginSchema
    ) -> TokenSchema:

        user = UserRepository.get_user_by_email(
            db=db,
            email=credentials.email
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        password_valid = verify_password(
            credentials.password,
            user.password
        )

        if not password_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role
            },
            expires_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id)
            }
        )

        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    @staticmethod
    def refresh_access_token(
        refresh_token: str
    ) -> TokenSchema:

        payload = verify_token(refresh_token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        user_id = payload.get("sub")

        access_token = create_access_token(
            data={
                "sub": user_id
            }
        )

        new_refresh_token = create_refresh_token(
            data={
                "sub": user_id
            }
        )

        return TokenSchema(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    @staticmethod
    def get_current_user(
        db: Session,
        token: str
    )  -> UserResponseSchema:

        payload = verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user_id = payload.get("sub")

        user = UserRepository.get_user_by_id(
            db=db,
            user_id=int(user_id)
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return UserResponseSchema.model_validate(user)