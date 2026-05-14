from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import Lamp, Room, User, UserRole
from app.schemas.lamp import LampRead
from app.schemas.room import RoomRead
from app.services.access import can_access_room, professor_room_ids

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomRead])
def list_rooms(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Room]:
    stmt = select(Room).order_by(Room.id)
    if user.role == UserRole.professor:
        ids = professor_room_ids(db, user)
        if not ids:
            return []
        stmt = stmt.where(Room.id.in_(ids))
    return list(db.scalars(stmt).all())


@router.get("/{room_id}/lamps", response_model=list[LampRead])
def list_room_lamps(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Lamp]:
    if not can_access_room(db, user, room_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this room")
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    stmt = select(Lamp).where(Lamp.room_id == room_id).order_by(Lamp.slot, Lamp.id)
    return list(db.scalars(stmt).all())
