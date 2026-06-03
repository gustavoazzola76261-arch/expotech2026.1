import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.database import SessionLocal
from app.models import Lamp, LampSchedule
from app.models.enums import LampAction, ScheduleScope
from app.services.access import set_lamp_state

logger = logging.getLogger(__name__)


def _campus_now() -> datetime:
    tz = ZoneInfo(get_settings().campus_timezone)
    return datetime.now(tz).replace(second=0, microsecond=0)


def _runs_on_weekday(schedule: LampSchedule, now: datetime) -> bool:
    if not schedule.days_of_week:
        return True
    return now.weekday() in schedule.days_of_week


def _lamps_for_schedule(db: Session, schedule: LampSchedule) -> list[Lamp]:
    if schedule.scope == ScheduleScope.all:
        return list(db.scalars(select(Lamp)).all())
    if schedule.scope == ScheduleScope.room and schedule.room_id is not None:
        return list(db.scalars(select(Lamp).where(Lamp.room_id == schedule.room_id)).all())
    if schedule.scope == ScheduleScope.rooms_group and schedule.room_ids:
        return list(db.scalars(select(Lamp).where(Lamp.room_id.in_(schedule.room_ids))).all())
    if schedule.scope == ScheduleScope.lamp and schedule.lamp_id is not None:
        lamp = db.get(Lamp, schedule.lamp_id)
        return [lamp] if lamp else []
    if schedule.scope == ScheduleScope.lamps_group and schedule.lamp_ids:
        return list(db.scalars(select(Lamp).where(Lamp.id.in_(schedule.lamp_ids))).all())
    return []


def run_due_schedules() -> None:
    now = _campus_now()
    db = SessionLocal()
    try:
        schedules = db.scalars(
            select(LampSchedule)
            .where(LampSchedule.is_enabled.is_(True))
            .options(joinedload(LampSchedule.room), joinedload(LampSchedule.lamp))
        ).all()

        for schedule in schedules:
            if schedule.hour != now.hour or schedule.minute != now.minute:
                continue
            if not _runs_on_weekday(schedule, now):
                continue
            if schedule.last_triggered_at is not None:
                last = schedule.last_triggered_at
                if last.tzinfo is None:
                    last = last.replace(tzinfo=now.tzinfo)
                else:
                    last = last.astimezone(now.tzinfo)
                if (
                    last.year == now.year
                    and last.month == now.month
                    and last.day == now.day
                    and last.hour == now.hour
                    and last.minute == now.minute
                ):
                    continue

            turn_on = schedule.action == LampAction.on
            lamps = _lamps_for_schedule(db, schedule)
            for lamp in lamps:
                if turn_on and lamp.is_on:
                    continue
                if not turn_on and not lamp.is_on:
                    continue
                set_lamp_state(db, lamp, turn_on=turn_on, user=None)

            schedule.last_triggered_at = now
            logger.info("Schedule %s (%s) applied to %d lamp(s)", schedule.id, schedule.name, len(lamps))

        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Erro ao executar programações")
    finally:
        db.close()
