from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload

from app.core.api_errors import conflict, not_found
from app.models import Lamp, Room, UserRoom
from app.schemas.room import AcConfigInput, LampConfigInput
from app.services.ac import ac_specs_from_count, sync_room_acs


def _sync_room_id_sequence(db: Session) -> None:
    db.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('rooms', 'id'), "
            "COALESCE((SELECT MAX(id) FROM rooms), 1), true)"
        )
    )


def _lamp_specs_from_count(count: int, default_power_watts: int) -> list[LampConfigInput]:
    return [LampConfigInput(power_watts=default_power_watts) for _ in range(count)]


def sync_room_lamps(db: Session, room_id: int, lamp_specs: list[LampConfigInput]) -> None:
    room = db.scalars(select(Room).where(Room.id == room_id).options(selectinload(Room.lamps))).first()
    if not room:
        raise not_found(log_detail=f"sync lamps room_id={room_id}")

    existing = sorted(room.lamps, key=lambda lamp: (lamp.slot, lamp.id))
    target = len(lamp_specs)

    for index, spec in enumerate(lamp_specs):
        slot = index + 1
        if index < len(existing):
            lamp = existing[index]
            lamp.slot = slot
            lamp.power_watts = spec.power_watts
            lamp.name = f"Lâmpada {slot}"
        else:
            db.add(
                Lamp(
                    room_id=room_id,
                    name=f"Lâmpada {slot}",
                    slot=slot,
                    power_watts=spec.power_watts,
                    is_on=False,
                )
            )

    for lamp in existing[target:]:
        db.delete(lamp)


def create_room_with_optional_id(
    db: Session,
    *,
    name: str,
    code: str,
    room_id: int | None = None,
    lamp_count: int = 3,
    default_power_watts: int = 20,
    ac_count: int = 1,
    default_ac_power_watts: int = 1500,
) -> Room:
    code = code.strip().upper()
    exists = db.scalars(select(Room).where(Room.code == code)).first()
    if exists:
        raise conflict(public_key="room_code_taken", log_detail=f"code={code}")

    if room_id is not None:
        if db.get(Room, room_id):
            raise conflict(public_key="room_id_taken", log_detail=f"room_id={room_id}")
        room = Room(id=room_id, name=name.strip(), code=code)
    else:
        room = Room(name=name.strip(), code=code)

    db.add(room)
    db.flush()
    specs = _lamp_specs_from_count(lamp_count, default_power_watts)
    sync_room_lamps(db, room.id, specs)
    if ac_count > 0:
        sync_room_acs(db, room.id, ac_specs_from_count(ac_count, default_ac_power_watts))
    db.commit()
    _sync_room_id_sequence(db)
    db.commit()
    db.refresh(room)
    return room


def update_room_details(
    db: Session,
    room_id: int,
    *,
    name: str | None = None,
    code: str | None = None,
    lamps: list[LampConfigInput] | None = None,
    air_conditioners: list[AcConfigInput] | None = None,
) -> Room:
    room = db.get(Room, room_id)
    if not room:
        raise not_found(log_detail=f"update room id={room_id}")

    if code is not None:
        code_norm = code.strip().upper()
        other = db.scalars(select(Room).where(Room.code == code_norm, Room.id != room_id)).first()
        if other:
            raise conflict(public_key="room_code_taken", log_detail=f"code={code_norm}")
        room.code = code_norm
    if name is not None:
        room.name = name.strip()

    if lamps is not None:
        sync_room_lamps(db, room_id, lamps)
    if air_conditioners is not None:
        sync_room_acs(db, room_id, air_conditioners)

    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room_id: int) -> None:
    room = db.get(Room, room_id)
    if not room:
        raise not_found(log_detail=f"delete room id={room_id}")
    db.delete(room)
    db.commit()
    _sync_room_id_sequence(db)
    db.commit()
