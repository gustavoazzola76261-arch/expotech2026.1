from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.api_errors import not_found, validation
from app.models import AcActuationLog, AirConditioner, Room, User
from app.models.air_conditioner import (
    DEFAULT_AC_POWER_W,
    DEFAULT_AC_TEMP_C,
    MAX_AC_TEMP_C,
    MIN_AC_TEMP_C,
)
from app.models.enums import LampAction
from app.schemas.room import AcConfigInput


def set_ac_state(
    db: Session,
    ac: AirConditioner,
    turn_on: bool,
    user: User | None = None,
) -> AcActuationLog:
    now = datetime.now(timezone.utc)
    energy_kwh: Decimal | None = None

    if turn_on:
        if not ac.is_on:
            ac.is_on = True
            ac.last_on_at = now
        action = LampAction.on
    else:
        if ac.is_on and ac.last_on_at is not None:
            elapsed_h = (now - ac.last_on_at).total_seconds() / 3600.0
            energy_kwh = Decimal(str(ac.power_watts * elapsed_h / 1000.0))
        ac.is_on = False
        ac.last_on_at = None
        action = LampAction.off

    log = AcActuationLog(
        user_id=user.id if user else None,
        air_conditioner_id=ac.id,
        action=action,
        energy_kwh=energy_kwh,
    )
    db.add(log)
    db.flush()
    return log


def sync_room_acs(db: Session, room_id: int, ac_specs: list[AcConfigInput]) -> None:
    room = db.scalars(
        select(Room).where(Room.id == room_id).options(selectinload(Room.air_conditioners))
    ).first()
    if not room:
        raise not_found(log_detail=f"sync ac room_id={room_id}")

    existing = sorted(room.air_conditioners, key=lambda unit: (unit.slot, unit.id))
    target = len(ac_specs)

    for index, spec in enumerate(ac_specs):
        slot = index + 1
        if index < len(existing):
            unit = existing[index]
            unit.slot = slot
            unit.power_watts = spec.power_watts
            unit.name = f"Ar {slot}"
        else:
            db.add(
                AirConditioner(
                    room_id=room_id,
                    name=f"Ar {slot}",
                    slot=slot,
                    power_watts=spec.power_watts,
                    is_on=False,
                    target_temp_c=DEFAULT_AC_TEMP_C,
                )
            )

    for unit in existing[target:]:
        db.delete(unit)


def set_ac_power(db: Session, ac: AirConditioner, *, turn_on: bool, user: User | None = None) -> AirConditioner:
    set_ac_state(db, ac, turn_on=turn_on, user=user)
    db.flush()
    return ac


def set_ac_temperature(db: Session, ac: AirConditioner, target_temp_c: int) -> AirConditioner:
    if not MIN_AC_TEMP_C <= target_temp_c <= MAX_AC_TEMP_C:
        raise validation(
            public_key="ac_temp_invalid",
            log_detail=f"temp={target_temp_c} range={MIN_AC_TEMP_C}-{MAX_AC_TEMP_C}",
        )
    ac.target_temp_c = target_temp_c
    db.flush()
    return ac


def turn_off_all_acs(db: Session, room_id: int | None = None) -> int:
    stmt = select(AirConditioner).where(AirConditioner.is_on.is_(True))
    if room_id is not None:
        stmt = stmt.where(AirConditioner.room_id == room_id)
    units = db.scalars(stmt).all()
    count = 0
    for unit in units:
        set_ac_state(db, unit, turn_on=False, user=None)
        count += 1
    db.commit()
    return count


def turn_on_all_acs(db: Session, room_id: int | None = None) -> int:
    stmt = select(AirConditioner).where(AirConditioner.is_on.is_(False))
    if room_id is not None:
        stmt = stmt.where(AirConditioner.room_id == room_id)
    units = db.scalars(stmt).all()
    count = 0
    for unit in units:
        set_ac_state(db, unit, turn_on=True, user=None)
        count += 1
    db.commit()
    return count


def ac_specs_from_count(count: int, default_power_watts: int = DEFAULT_AC_POWER_W) -> list[AcConfigInput]:
    return [AcConfigInput(power_watts=default_power_watts) for _ in range(count)]
