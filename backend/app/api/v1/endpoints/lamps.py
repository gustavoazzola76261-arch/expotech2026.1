from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import Lamp, User
from app.schemas.lamp import LampCommand, LampRead
from app.services.access import can_control_lamp, set_lamp_state

router = APIRouter(prefix="/lamps", tags=["lamps"])


@router.get("/{lamp_id}", response_model=LampRead)
def get_lamp(
    lamp_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Lamp:
    lamp = db.get(Lamp, lamp_id)
    if not lamp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lamp not found")
    if not can_control_lamp(db, user, lamp):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this lamp")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lamp not found")
    if not can_control_lamp(db, user, lamp):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this lamp")
    turn_on = body.action == "on"
    set_lamp_state(db, user, lamp, turn_on=turn_on)
    db.commit()
    db.refresh(lamp)
    return lamp
