from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, require_roles
from app.core.api_errors import forbidden, not_found
from app.database import get_db
from app.models import AirConditioner, Lamp, Room, User, UserRole
from app.schemas.ac import AirConditionerRead
from app.schemas.errors import ActionResult
from app.schemas.lamp import LampRead
from app.schemas.room import RoomCreate, RoomOverview, RoomRead, RoomUpdate
from app.services.access import can_access_room, professor_room_ids, turn_off_all_lamps, turn_on_all_lamps
from app.services.ac import turn_off_all_acs, turn_on_all_acs
from app.services.rooms import create_room_with_optional_id, delete_room, update_room_details

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _require_room(db: Session, user: User, room_id: int) -> Room:
    if not can_access_room(db, user, room_id):
        raise forbidden(log_detail=f"room access denied room_id={room_id} user={user.id}")
    room = db.get(Room, room_id)
    if not room:
        raise not_found(log_detail=f"room id={room_id}")
    return room


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
    stmt = (
        select(Room)
        .options(selectinload(Room.lamps), selectinload(Room.air_conditioners))
        .order_by(Room.id)
    )
    if user.role == UserRole.professor:
        ids = professor_room_ids(db, user)
        if not ids:
            return []
        stmt = stmt.where(Room.id.in_(ids))
    rooms = db.scalars(stmt).unique().all()
    result: list[RoomOverview] = []
    for room in rooms:
        lamps = sorted(room.lamps, key=lambda lamp: (lamp.slot, lamp.id))
        acs = sorted(room.air_conditioners, key=lambda unit: (unit.slot, unit.id))
        result.append(
            RoomOverview(
                id=room.id,
                name=room.name,
                code=room.code,
                lamps=[LampRead.model_validate(lamp) for lamp in lamps],
                air_conditioners=[AirConditionerRead.model_validate(unit) for unit in acs],
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
        lamp_count=payload.lamp_count,
        default_power_watts=payload.default_power_watts,
        ac_count=payload.ac_count,
        default_ac_power_watts=payload.default_ac_power_watts,
    )


@router.patch("/{room_id}", response_model=RoomRead)
def update_room(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> Room:
    return update_room_details(
        db,
        room_id,
        name=payload.name,
        code=payload.code,
        lamps=payload.lamps,
        air_conditioners=payload.air_conditioners,
    )


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> None:
    delete_room(db, room_id)


@router.post("/{room_id}/lamps/all-off", response_model=ActionResult)
def room_all_lamps_off(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ActionResult:
    _require_room(db, user, room_id)
    count = turn_off_all_lamps(db, room_id=room_id)
    return ActionResult(message="Comando enviado: desligar lâmpadas da sala.", data={"turned_off": count})


@router.post("/{room_id}/lamps/all-on", response_model=ActionResult)
def room_all_lamps_on(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ActionResult:
    _require_room(db, user, room_id)
    count = turn_on_all_lamps(db, room_id=room_id)
    return ActionResult(message="Comando enviado: ligar lâmpadas da sala.", data={"turned_on": count})


@router.post("/{room_id}/ac/all-off", response_model=ActionResult)
def room_all_ac_off(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ActionResult:
    _require_room(db, user, room_id)
    count = turn_off_all_acs(db, room_id=room_id)
    return ActionResult(message="Comando enviado: desligar ar da sala.", data={"turned_off": count})


@router.post("/{room_id}/ac/all-on", response_model=ActionResult)
def room_all_ac_on(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ActionResult:
    _require_room(db, user, room_id)
    count = turn_on_all_acs(db, room_id=room_id)
    return ActionResult(message="Comando enviado: ligar ar da sala.", data={"turned_on": count})


@router.get("/{room_id}/ac", response_model=list[AirConditionerRead])
def list_room_ac(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[AirConditioner]:
    _require_room(db, user, room_id)
    stmt = (
        select(AirConditioner)
        .where(AirConditioner.room_id == room_id)
        .order_by(AirConditioner.slot, AirConditioner.id)
    )
    return list(db.scalars(stmt).all())


@router.get("/{room_id}/lamps", response_model=list[LampRead])
def list_room_lamps(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Lamp]:
    _require_room(db, user, room_id)
    stmt = select(Lamp).where(Lamp.room_id == room_id).order_by(Lamp.slot, Lamp.id)
    return list(db.scalars(stmt).all())
