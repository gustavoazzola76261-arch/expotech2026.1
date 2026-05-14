from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database import get_db
from app.models import User, UserRole
from app.schemas.user import UserCreate, UserReadAdmin, UserUpdate
from app.services.access import professor_room_ids
from app.services.user_admin import apply_user_update
from app.services.users import create_user

router = APIRouter(prefix="/admin/users", tags=["admin"])


def _user_to_admin_read(db: Session, user: User) -> UserReadAdmin:
    rids = sorted(professor_room_ids(db, user)) if user.role == UserRole.professor else []
    return UserReadAdmin(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        room_ids=rids,
    )


@router.get("", response_model=list[UserReadAdmin])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
) -> list[UserReadAdmin]:
    users = db.scalars(select(User).order_by(User.id)).all()
    return [_user_to_admin_read(db, u) for u in users]


@router.post("", response_model=UserReadAdmin, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
) -> UserReadAdmin:
    email = payload.email.lower().strip()
    exists = db.scalars(select(User).where(User.email == email)).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if payload.role == UserRole.professor and not payload.room_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Professors must be linked to at least one room",
        )
    if payload.role != UserRole.professor and payload.room_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="room_ids only applies to professor role",
        )
    user = create_user(
        db,
        email=email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
        room_ids=payload.room_ids if payload.role == UserRole.professor else None,
    )
    return _user_to_admin_read(db, user)


@router.patch("/{user_id}", response_model=UserReadAdmin)
def update_user_admin(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles(UserRole.admin)),
) -> UserReadAdmin:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    apply_user_update(db, user=user, payload=payload, admin=admin)
    db.commit()
    db.refresh(user)
    return _user_to_admin_read(db, user)
