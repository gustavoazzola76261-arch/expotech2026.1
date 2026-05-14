from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models import User, UserRole, UserRoom
from app.schemas.user import UserUpdate


def _clear_user_rooms(db: Session, user_id: int) -> None:
    db.execute(delete(UserRoom).where(UserRoom.user_id == user_id))


def _set_user_rooms_no_commit(db: Session, user_id: int, room_ids: list[int]) -> None:
    _clear_user_rooms(db, user_id)
    for rid in room_ids:
        db.add(UserRoom(user_id=user_id, room_id=rid))


def apply_user_update(
    db: Session,
    *,
    user: User,
    payload: UserUpdate,
    admin: User,
) -> None:
    if user.id == admin.id:
        if payload.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode desativar a própria conta",
            )
        if payload.role is not None and payload.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode remover o próprio perfil de administrador",
            )

    was_professor = user.role == UserRole.professor

    if payload.email is not None:
        new_email = payload.email.lower().strip()
        if new_email != user.email:
            exists = db.scalars(select(User).where(User.email == new_email)).first()
            if exists:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")
        user.email = new_email

    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()

    if payload.is_active is not None:
        user.is_active = payload.is_active

    if payload.password is not None:
        user.hashed_password = hash_password(payload.password)

    if payload.role is not None:
        user.role = payload.role

    eff_role = user.role

    if eff_role != UserRole.professor:
        _clear_user_rooms(db, user.id)
    else:
        if payload.room_ids is not None:
            if not payload.room_ids:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Professor deve ter ao menos uma sala vinculada",
                )
            _set_user_rooms_no_commit(db, user.id, payload.room_ids)
        elif not was_professor:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Ao tornar usuário professor, informe room_ids com ao menos uma sala",
            )
