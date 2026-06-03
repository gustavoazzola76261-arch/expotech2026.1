from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import verify_esp32_device
from app.rate_limit import LIMIT_IOT_POLL, limiter
from app.database import get_db
from app.models import AirConditioner, Lamp, Room
from app.schemas.iot import IoTAcState, IoTStateResponse, IoTLampState

router = APIRouter(prefix="/iot", tags=["iot"])


@router.get("/state", response_model=IoTStateResponse, dependencies=[Depends(verify_esp32_device)])
@limiter.limit(LIMIT_IOT_POLL)
def get_iot_state(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    room_ids: str = Query(..., description="IDs das salas separados por vírgula, ex: 1,2"),
) -> IoTStateResponse:
    try:
        ids = [int(x.strip()) for x in room_ids.split(",") if x.strip()]
    except ValueError:
        ids = []
    if not ids:
        return IoTStateResponse(lamps=[], air_conditioners=[], poll_interval_ms=2000)

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

    ac_stmt = (
        select(AirConditioner)
        .options(joinedload(AirConditioner.room))
        .where(AirConditioner.room_id.in_(ids))
        .order_by(AirConditioner.room_id, AirConditioner.slot, AirConditioner.id)
    )
    ac_units = db.scalars(ac_stmt).unique().all()
    by_room: dict[int, list[AirConditioner]] = {}
    for ac in ac_units:
        by_room.setdefault(ac.room_id, []).append(ac)

    ac_result: list[IoTAcState] = []
    for room_id in sorted(by_room.keys()):
        units = sorted(by_room[room_id], key=lambda u: (u.slot, u.id))
        primary = units[0]
        room = primary.room
        ac_result.append(
            IoTAcState(
                room_id=room_id,
                room_code=room.code if room else "",
                is_on=any(u.is_on for u in units),
                target_temp_c=primary.target_temp_c,
            )
        )

    return IoTStateResponse(lamps=result, air_conditioners=ac_result, poll_interval_ms=2000)
