from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActuationLog, Lamp, LampAction, Room, User, UserRole, UserRoom


def professor_room_ids(db: Session, user: User) -> set[int]:
    rows = db.scalars(select(UserRoom.room_id).where(UserRoom.user_id == user.id)).all()
    return set(rows)


def can_access_room(db: Session, user: User, room_id: int) -> bool:
    if user.role == UserRole.admin or user.role == UserRole.mestre:
        return True
    return room_id in professor_room_ids(db, user)


def can_control_lamp(db: Session, user: User, lamp: Lamp) -> bool:
    return can_access_room(db, user, lamp.room_id)


def set_lamp_state(
    db: Session,
    lamp: Lamp,
    turn_on: bool,
    user: User | None = None,
) -> ActuationLog:
    now = datetime.now(timezone.utc)
    energy_kwh: Decimal | None = None

    if turn_on:
        if not lamp.is_on:
            lamp.is_on = True
            lamp.last_on_at = now
        action = LampAction.on
    else:
        if lamp.is_on and lamp.last_on_at is not None:
            elapsed_h = (now - lamp.last_on_at).total_seconds() / 3600.0
            energy_kwh = Decimal(str(lamp.power_watts * elapsed_h / 1000.0))
        lamp.is_on = False
        lamp.last_on_at = None
        action = LampAction.off

    log = ActuationLog(
        user_id=user.id if user else None,
        lamp_id=lamp.id,
        action=action,
        energy_kwh=energy_kwh,
    )
    db.add(log)
    db.flush()
    return log


def turn_off_all_lamps(db: Session, room_id: int | None = None) -> int:
    stmt = select(Lamp).where(Lamp.is_on.is_(True))
    if room_id is not None:
        stmt = stmt.where(Lamp.room_id == room_id)
    lamps = db.scalars(stmt).all()
    count = 0
    for lamp in lamps:
        set_lamp_state(db, lamp, turn_on=False, user=None)
        count += 1
    db.commit()
    return count


def turn_on_all_lamps(db: Session, room_id: int | None = None) -> int:
    stmt = select(Lamp).where(Lamp.is_on.is_(False))
    if room_id is not None:
        stmt = stmt.where(Lamp.room_id == room_id)
    lamps = db.scalars(stmt).all()
    count = 0
    for lamp in lamps:
        set_lamp_state(db, lamp, turn_on=True, user=None)
        count += 1
    db.commit()
    return count
