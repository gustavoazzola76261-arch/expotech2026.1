from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, require_roles
from app.database import get_db
from app.models import Lamp, Room, User, UserRole
from app.schemas.lamp import LampRead
from app.schemas.room import RoomCreate, RoomOverview, RoomRead, RoomUpdate
from app.services.access import can_access_room, professor_room_ids, turn_off_all_lamps, turn_on_all_lamps
from app.services.rooms import change_room_id, create_room_with_optional_id

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


@router.get("/overview", response_model=list[RoomOverview])
def rooms_overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[RoomOverview]:
    stmt = select(Room).options(selectinload(Room.lamps)).order_by(Room.id)
    if user.role == UserRole.professor:
        ids = professor_room_ids(db, user)
        if not ids:
            return []
        stmt = stmt.where(Room.id.in_(ids))
    rooms = db.scalars(stmt).unique().all()
    result: list[RoomOverview] = []
    for room in rooms:
        lamps = sorted(room.lamps, key=lambda lamp: (lamp.slot, lamp.id))
        result.append(
            RoomOverview(
                id=room.id,
                name=room.name,
                code=room.code,
                lamps=[LampRead.model_validate(lamp) for lamp in lamps],
            )
        )
    return result


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> Room:
    return create_room_with_optional_id(
        db,
        name=payload.name,
        code=payload.code,
        room_id=payload.id,
    )


@router.patch("/{room_id}", response_model=RoomRead)
def update_room(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> Room:
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    if payload.new_id is not None:
        room = change_room_id(db, room_id, payload.new_id)
        room_id = room.id

    if payload.code is not None:
        code = payload.code.strip().upper()
        other = db.scalars(select(Room).where(Room.code == code, Room.id != room_id)).first()
        if other:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Código de sala já existe")
        room.code = code
    if payload.name is not None:
        room.name = payload.name.strip()

    db.commit()
    db.refresh(room)
    return room


@router.post("/{room_id}/lamps/all-off")
def room_all_lamps_off(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> dict[str, int]:
    if not can_access_room(db, user, room_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso à sala")
    if not db.get(Room, room_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    count = turn_off_all_lamps(db, room_id=room_id)
    return {"turned_off": count}


@router.post("/{room_id}/lamps/all-on")
def room_all_lamps_on(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> dict[str, int]:
    if not can_access_room(db, user, room_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso à sala")
    if not db.get(Room, room_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    count = turn_on_all_lamps(db, room_id=room_id)
    return {"turned_on": count}


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
