from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_roles
from app.database import get_db
from app.models import ActuationLog, Lamp, User, UserRole
from app.schemas.actuation import ActuationHistoryRead

router = APIRouter(prefix="/admin/actuations", tags=["admin"])


@router.get("", response_model=list[ActuationHistoryRead])
def list_actuation_history(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[ActuationHistoryRead]:
    stmt = (
        select(ActuationLog)
        .options(
            joinedload(ActuationLog.user),
            joinedload(ActuationLog.lamp).joinedload(Lamp.room),
        )
        .order_by(ActuationLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    logs = db.scalars(stmt).unique().all()

    out: list[ActuationHistoryRead] = []
    for log in logs:
        lamp = log.lamp
        room = lamp.room if lamp else None
        user = log.user
        out.append(
            ActuationHistoryRead(
                id=log.id,
                created_at=log.created_at,
                action=log.action,
                energy_kwh=log.energy_kwh,
                user_id=log.user_id,
                user_name=user.full_name if user else None,
                user_email=user.email if user else None,
                room_id=room.id if room else (lamp.room_id if lamp else 0),
                room_name=room.name if room else "—",
                room_code=room.code if room else "—",
                lamp_id=lamp.id if lamp else log.lamp_id,
                lamp_name=lamp.name if lamp else "—",
                lamp_slot=lamp.slot if lamp else 0,
            )
        )
    return out
