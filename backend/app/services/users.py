from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User, UserRole, UserRoom


def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    role: UserRole,
    room_ids: list[int] | None = None,
) -> User:
    user = User(
        email=email.lower().strip(),
        hashed_password=hash_password(password),
        full_name=full_name.strip(),
        role=role,
    )
    db.add(user)
    db.flush()
    if role == UserRole.professor and room_ids:
        for rid in room_ids:
            db.add(UserRoom(user_id=user.id, room_id=rid))
    db.commit()
    db.refresh(user)
    return user


def set_user_rooms(db: Session, user: User, room_ids: list[int]) -> None:
    db.execute(delete(UserRoom).where(UserRoom.user_id == user.id))
    for rid in room_ids:
        db.add(UserRoom(user_id=user.id, room_id=rid))
    db.commit()
