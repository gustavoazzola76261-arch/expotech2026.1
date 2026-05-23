from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.api_errors import forbidden, not_found
from app.database import get_db
from app.models import Lamp, User, UserRole
from app.schemas.errors import ActionResult
from app.schemas.lamp import LampCommand, LampRead
from app.services.access import can_control_lamp, set_lamp_state, turn_off_all_lamps, turn_on_all_lamps

router = APIRouter(prefix="/lamps", tags=["lamps"])


@router.post("/all-off", response_model=ActionResult)
def all_lamps_off(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ActionResult:
    count = turn_off_all_lamps(db, room_id=None)
    return ActionResult(message="Comando enviado: desligar todas as lâmpadas.", data={"turned_off": count})


@router.post("/all-on", response_model=ActionResult)
def all_lamps_on(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ActionResult:
    count = turn_on_all_lamps(db, room_id=None)
    return ActionResult(message="Comando enviado: ligar todas as lâmpadas.", data={"turned_on": count})


@router.get("/{lamp_id}", response_model=LampRead)
def get_lamp(
    lamp_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Lamp:
    lamp = db.get(Lamp, lamp_id)
    if not lamp:
        raise not_found(log_detail=f"lamp id={lamp_id}")
    if not can_control_lamp(db, user, lamp):
        raise forbidden(log_detail=f"lamp id={lamp_id} room={lamp.room_id} user={user.id}")
    return lamp


@router.post("/{lamp_id}/command", response_model=LampRead)
def command_lamp(
    lamp_id: int,
    body: LampCommand,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Lamp:
    lamp = db.get(Lamp, lamp_id)
    if not lamp:
        raise not_found(log_detail=f"lamp id={lamp_id}")
    if not can_control_lamp(db, user, lamp):
        raise forbidden(log_detail=f"lamp command id={lamp_id}")
    turn_on = body.action == "on"
    set_lamp_state(db, lamp, turn_on=turn_on, user=user)
    db.commit()
    db.refresh(lamp)
    return lamp
