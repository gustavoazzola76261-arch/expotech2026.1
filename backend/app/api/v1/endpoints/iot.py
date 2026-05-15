from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import verify_esp32_device
from app.database import get_db
from app.models import Lamp, Room
from app.schemas.iot import IoTStateResponse, IoTLampState

router = APIRouter(prefix="/iot", tags=["iot"])


@router.get("/state", response_model=IoTStateResponse, dependencies=[Depends(verify_esp32_device)])
def get_iot_state(
    db: Session = Depends(get_db),
    room_ids: str = Query(..., description="IDs das salas separados por vírgula, ex: 1,2"),
) -> IoTStateResponse:
    try:
        ids = [int(x.strip()) for x in room_ids.split(",") if x.strip()]
    except ValueError:
        ids = []
    if not ids:
        return IoTStateResponse(lamps=[], poll_interval_ms=2000)

    stmt = (
        select(Lamp)
        .options(joinedload(Lamp.room))
        .join(Room, Lamp.room_id == Room.id)
        .where(Lamp.room_id.in_(ids))
        .order_by(Lamp.room_id, Lamp.slot, Lamp.id)
    )
    lamps = db.scalars(stmt).unique().all()

    result: list[IoTLampState] = []
    for lamp in lamps:
        room = lamp.room
        result.append(
            IoTLampState(
                lamp_id=lamp.id,
                room_id=lamp.room_id,
                room_code=room.code if room else "",
                room_name=room.name if room else "",
                slot=lamp.slot,
                name=lamp.name,
                is_on=lamp.is_on,
            )
        )
    return IoTStateResponse(lamps=result, poll_interval_ms=2000)
