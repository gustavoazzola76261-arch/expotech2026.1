from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_roles
from app.core.api_errors import not_found, validation
from app.database import get_db
from app.models import Lamp, LampSchedule, Room, User, UserRole
from app.models.enums import ScheduleScope
from app.schemas.schedule import WEEKDAY_LABELS, ScheduleCreate, ScheduleRead, ScheduleUpdate

router = APIRouter(prefix="/schedules", tags=["schedules"])


def _target_label(schedule: LampSchedule, db: Session) -> str:
    if schedule.scope == ScheduleScope.all:
        return "Todas as lâmpadas"
    if schedule.scope == ScheduleScope.room:
        return f"Sala: {schedule.room.name}" if schedule.room else f"Sala ID {schedule.room_id}"
    if schedule.scope == ScheduleScope.rooms_group and schedule.room_ids:
        names = db.scalars(select(Room.name).where(Room.id.in_(schedule.room_ids))).all()
        if names:
            return f"Grupo de salas: {', '.join(names)}"
        return f"Grupo de salas (IDs {schedule.room_ids})"
    if schedule.scope == ScheduleScope.lamp:
        return f"Lâmpada: {schedule.lamp.name}" if schedule.lamp else f"Lâmpada ID {schedule.lamp_id}"
    if schedule.scope == ScheduleScope.lamps_group and schedule.lamp_ids:
        names = db.scalars(select(Lamp.name).where(Lamp.id.in_(schedule.lamp_ids))).all()
        if names:
            return f"Grupo de lâmpadas: {', '.join(names)}"
        return f"Grupo de lâmpadas (IDs {schedule.lamp_ids})"
    return "—"


def _days_label(days: list[int] | None) -> str:
    if not days:
        return "Todos os dias"
    return ", ".join(WEEKDAY_LABELS[d] for d in sorted(days))


def _to_read(schedule: LampSchedule, db: Session) -> ScheduleRead:
    days = list(schedule.days_of_week) if schedule.days_of_week else None
    return ScheduleRead(
        id=schedule.id,
        name=schedule.name,
        scope=schedule.scope,
        action=schedule.action,
        hour=schedule.hour,
        minute=schedule.minute,
        room_id=schedule.room_id,
        lamp_id=schedule.lamp_id,
        room_ids=list(schedule.room_ids) if schedule.room_ids else None,
        lamp_ids=list(schedule.lamp_ids) if schedule.lamp_ids else None,
        days_of_week=days,
        days_label=_days_label(days),
        is_enabled=schedule.is_enabled,
        room_name=schedule.room.name if schedule.room else None,
        lamp_name=schedule.lamp.name if schedule.lamp else None,
        target_label=_target_label(schedule, db),
    )


def _apply_scope_cleanup(schedule: LampSchedule) -> None:
    if schedule.scope == ScheduleScope.all:
        schedule.room_id = None
        schedule.lamp_id = None
        schedule.room_ids = None
        schedule.lamp_ids = None
    elif schedule.scope == ScheduleScope.room:
        schedule.room_ids = None
        schedule.lamp_ids = None
        schedule.lamp_id = None
    elif schedule.scope == ScheduleScope.rooms_group:
        schedule.room_id = None
        schedule.lamp_id = None
        schedule.lamp_ids = None
    elif schedule.scope == ScheduleScope.lamp:
        schedule.room_id = None
        schedule.room_ids = None
        schedule.lamp_ids = None
    elif schedule.scope == ScheduleScope.lamps_group:
        schedule.room_id = None
        schedule.lamp_id = None
        schedule.room_ids = None


@router.get("", response_model=list[ScheduleRead])
def list_schedules(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> list[ScheduleRead]:
    stmt = (
        select(LampSchedule)
        .options(joinedload(LampSchedule.room), joinedload(LampSchedule.lamp))
        .order_by(LampSchedule.hour, LampSchedule.minute, LampSchedule.id)
    )
    rows = db.scalars(stmt).unique().all()
    return [_to_read(s, db) for s in rows]


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ScheduleRead:
    _validate_targets(db, payload.scope, payload.room_id, payload.lamp_id, payload.room_ids, payload.lamp_ids)
    schedule = LampSchedule(
        name=payload.name.strip(),
        scope=payload.scope,
        action=payload.action,
        hour=payload.hour,
        minute=payload.minute,
        room_id=payload.room_id,
        lamp_id=payload.lamp_id,
        room_ids=payload.room_ids,
        lamp_ids=payload.lamp_ids,
        days_of_week=payload.days_of_week,
        is_enabled=payload.is_enabled,
        created_by_id=user.id,
    )
    _apply_scope_cleanup(schedule)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    schedule = db.scalars(
        select(LampSchedule)
        .where(LampSchedule.id == schedule.id)
        .options(joinedload(LampSchedule.room), joinedload(LampSchedule.lamp))
    ).first()
    return _to_read(schedule, db)


@router.patch("/{schedule_id}", response_model=ScheduleRead)
def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> ScheduleRead:
    schedule = db.get(LampSchedule, schedule_id)
    if not schedule:
        raise not_found(log_detail=f"schedule id={schedule_id}")

    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        schedule.name = data["name"].strip()
    for field in (
        "scope",
        "action",
        "hour",
        "minute",
        "room_id",
        "lamp_id",
        "room_ids",
        "lamp_ids",
        "days_of_week",
        "is_enabled",
    ):
        if field in data:
            value = data[field]
            if field == "days_of_week":
                from app.schemas.schedule import normalize_days_of_week

                value = normalize_days_of_week(value)
            setattr(schedule, field, value)

    _validate_targets(
        db,
        schedule.scope,
        schedule.room_id,
        schedule.lamp_id,
        schedule.room_ids,
        schedule.lamp_ids,
    )
    _apply_scope_cleanup(schedule)

    db.commit()
    db.refresh(schedule)
    schedule = db.scalars(
        select(LampSchedule)
        .where(LampSchedule.id == schedule.id)
        .options(joinedload(LampSchedule.room), joinedload(LampSchedule.lamp))
    ).first()
    return _to_read(schedule, db)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.mestre)),
) -> None:
    schedule = db.get(LampSchedule, schedule_id)
    if not schedule:
        raise not_found(log_detail=f"schedule id={schedule_id}")
    db.delete(schedule)
    db.commit()


def _validate_targets(
    db: Session,
    scope: ScheduleScope,
    room_id: int | None,
    lamp_id: int | None,
    room_ids: list[int] | None,
    lamp_ids: list[int] | None,
) -> None:
    if scope == ScheduleScope.room:
        if room_id is None or not db.get(Room, room_id):
            raise validation(public_key="schedule_target_invalid", log_detail="schedule room target")
    elif scope == ScheduleScope.rooms_group:
        if not room_ids:
            raise validation(public_key="schedule_rooms_required", log_detail="schedule rooms group empty")
        for rid in room_ids:
            if not db.get(Room, rid):
                raise validation(
                    public_key="schedule_target_invalid",
                    log_detail=f"schedule invalid room_id={rid}",
                )
    elif scope == ScheduleScope.lamp:
        if lamp_id is None or not db.get(Lamp, lamp_id):
            raise validation(public_key="schedule_target_invalid", log_detail="schedule lamp target")
    elif scope == ScheduleScope.lamps_group:
        if not lamp_ids:
            raise validation(public_key="schedule_lamps_required", log_detail="schedule lamps group empty")
        for lid in lamp_ids:
            if not db.get(Lamp, lid):
                raise validation(
                    public_key="schedule_target_invalid",
                    log_detail=f"schedule invalid lamp_id={lid}",
                )
