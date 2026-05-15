from fastapi import HTTPException, status
from sqlalchemy import select, text, update
from sqlalchemy.orm import Session

from app.models import Lamp, Room, UserRoom


def _sync_room_id_sequence(db: Session) -> None:
    db.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('rooms', 'id'), "
            "COALESCE((SELECT MAX(id) FROM rooms), 1), true)"
        )
    )


def change_room_id(db: Session, old_id: int, new_id: int) -> Room:
    if old_id == new_id:
        room = db.get(Room, old_id)
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
        return room

    if db.get(Room, new_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"ID {new_id} já está em uso")

    room = db.get(Room, old_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    db.execute(update(UserRoom).where(UserRoom.room_id == old_id).values(room_id=new_id))
    db.execute(update(Lamp).where(Lamp.room_id == old_id).values(room_id=new_id))
    db.execute(update(Room).where(Room.id == old_id).values(id=new_id))
    db.commit()
    _sync_room_id_sequence(db)
    db.commit()
    updated = db.get(Room, new_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao alterar ID")
    return updated


def create_room_with_optional_id(
    db: Session,
    *,
    name: str,
    code: str,
    room_id: int | None = None,
) -> Room:
    code = code.strip().upper()
    exists = db.scalars(select(Room).where(Room.code == code)).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Código de sala já existe")

    if room_id is not None:
        if db.get(Room, room_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"ID {room_id} já está em uso")
        room = Room(id=room_id, name=name.strip(), code=code)
    else:
        room = Room(name=name.strip(), code=code)

    db.add(room)
    db.flush()
    for slot in range(1, 4):
        db.add(
            Lamp(
                room_id=room.id,
                name=f"Lâmpada {slot}",
                slot=slot,
                power_watts=20,
                is_on=False,
            )
        )
    db.commit()
    _sync_room_id_sequence(db)
    db.commit()
    db.refresh(room)
    return room
