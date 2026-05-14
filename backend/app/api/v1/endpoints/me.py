from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import User, UserRole
from app.schemas.user import UserReadAdmin
from app.services.access import professor_room_ids

router = APIRouter(prefix="/me", tags=["me"])


def _normalize_role(role: object) -> UserRole:
    if isinstance(role, UserRole):
        return role
    return UserRole(str(role))


@router.get("", response_model=UserReadAdmin)
def read_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UserReadAdmin:
    room_ids: list[int] = []
    if _normalize_role(user.role) == UserRole.professor:
        room_ids = sorted(professor_room_ids(db, user))
    return UserReadAdmin(
        id=user.id,
        email=(user.email or "").strip(),
        full_name=(user.full_name or "").strip(),
        role=_normalize_role(user.role),
        is_active=bool(user.is_active),
        room_ids=room_ids,
    )
