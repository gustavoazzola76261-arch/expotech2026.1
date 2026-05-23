from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.api_errors import forbidden, not_found
from app.database import get_db
from app.models import AirConditioner, User, UserRole
from app.schemas.ac import (
    AirConditionerCommandBody,
    AirConditionerRead,
    AirConditionerTemperatureUpdate,
)
from app.schemas.errors import ActionResult
from app.services.access import can_access_room
from app.services.ac import set_ac_power, set_ac_temperature, turn_off_all_acs, turn_on_all_acs

router = APIRouter(prefix="/ac", tags=["ac"])


@router.post("/all-off", response_model=ActionResult)
def all_ac_off(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ActionResult:
    count = turn_off_all_acs(db, room_id=None)
    return ActionResult(message="Comando enviado: desligar todos os aparelhos de ar.", data={"turned_off": count})


@router.post("/all-on", response_model=ActionResult)
def all_ac_on(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ActionResult:
    count = turn_on_all_acs(db, room_id=None)
    return ActionResult(message="Comando enviado: ligar todos os aparelhos de ar.", data={"turned_on": count})


@router.post("/{ac_id}/command", response_model=AirConditionerRead)
def command_ac(
    ac_id: int,
    body: AirConditionerCommandBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AirConditioner:
    ac = db.get(AirConditioner, ac_id)
    if not ac:
        raise not_found(log_detail=f"ac id={ac_id}")
    if not can_access_room(db, user, ac.room_id):
        raise forbidden(log_detail=f"ac command id={ac_id}")
    set_ac_power(db, ac, turn_on=body.action == "on", user=user)
    db.commit()
    db.refresh(ac)
    return ac


@router.patch("/{ac_id}/temperature", response_model=AirConditionerRead)
def set_ac_unit_temperature(
    ac_id: int,
    body: AirConditionerTemperatureUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> AirConditioner:
    ac = db.get(AirConditioner, ac_id)
    if not ac:
        raise not_found(log_detail=f"ac id={ac_id}")
    if not can_access_room(db, user, ac.room_id):
        raise forbidden(log_detail=f"ac temp id={ac_id}")
    set_ac_temperature(db, ac, body.target_temp_c)
    db.commit()
    db.refresh(ac)
    return ac
