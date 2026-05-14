from sqlalchemy.orm import Session

from app.database.models.user_model import (
    UserModel
)


class UserRepository:

    @staticmethod
    def create(
        db: Session,
        user_data: dict
    ):
        """
        Cria um novo usuário
        """

        user = UserModel(**user_data)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int
    ):
        """
        Busca usuário por ID
        """

        return db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ):
        """
        Busca usuário por email
        """

        return db.query(UserModel).filter(
            UserModel.email == email
        ).first()

    @staticmethod
    def get_all(
        db: Session
    ):
        """
        Lista todos os usuários
        """

        return db.query(UserModel).all()

    @staticmethod
    def update(
        db: Session,
        user: UserModel,
        update_data: dict
    ):
        """
        Atualiza usuário
        """

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete(
        db: Session,
        user: UserModel
    ):
        """
        Remove usuário
        """

        db.delete(user)
        db.commit()

        return True