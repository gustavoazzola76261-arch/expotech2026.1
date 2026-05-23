"""Agregação de consumo (lâmpadas + ar-condicionado)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AcActuationLog, ActuationLog, AirConditioner, Lamp


def _lamp_ids_subq(room_id: int | None):
    if room_id is not None:
        return select(Lamp.id).where(Lamp.room_id == room_id)
    return select(Lamp.id)


def _ac_ids_subq(room_id: int | None):
    if room_id is not None:
        return select(AirConditioner.id).where(AirConditioner.room_id == room_id)
    return select(AirConditioner.id)


def sum_total_energy_kwh(db: Session, *, room_id: int | None = None) -> Decimal:
    lamp_stmt = select(func.coalesce(func.sum(ActuationLog.energy_kwh), 0)).where(
        ActuationLog.energy_kwh.isnot(None),
        ActuationLog.lamp_id.in_(_lamp_ids_subq(room_id)),
    )
    ac_stmt = select(func.coalesce(func.sum(AcActuationLog.energy_kwh), 0)).where(
        AcActuationLog.energy_kwh.isnot(None),
        AcActuationLog.air_conditioner_id.in_(_ac_ids_subq(room_id)),
    )
    lamp_total = db.scalar(lamp_stmt) or 0
    ac_total = db.scalar(ac_stmt) or 0
    return Decimal(str(lamp_total)) + Decimal(str(ac_total))


def monthly_energy_by_key(
    db: Session,
    *,
    start: datetime,
    end: datetime,
    room_id: int | None = None,
) -> dict[str, Decimal]:
    lamp_bucket = func.date_trunc("month", ActuationLog.created_at)
    lamp_stmt = (
        select(lamp_bucket, func.coalesce(func.sum(ActuationLog.energy_kwh), 0))
        .where(
            ActuationLog.energy_kwh.isnot(None),
            ActuationLog.created_at >= start,
            ActuationLog.created_at <= end,
            ActuationLog.lamp_id.in_(_lamp_ids_subq(room_id)),
        )
        .group_by(lamp_bucket)
    )
    ac_bucket = func.date_trunc("month", AcActuationLog.created_at)
    ac_stmt = (
        select(ac_bucket, func.coalesce(func.sum(AcActuationLog.energy_kwh), 0))
        .where(
            AcActuationLog.energy_kwh.isnot(None),
            AcActuationLog.created_at >= start,
            AcActuationLog.created_at <= end,
            AcActuationLog.air_conditioner_id.in_(_ac_ids_subq(room_id)),
        )
        .group_by(ac_bucket)
    )

    by_month: dict[str, Decimal] = {}

    def _merge_rows(rows) -> None:
        for row in rows:
            b = row[0]
            if b is None:
                continue
            if b.tzinfo is None:
                from datetime import timezone

                b = b.replace(tzinfo=timezone.utc)
            key = f"{b.year:04d}-{b.month:02d}"
            by_month[key] = by_month.get(key, Decimal("0")) + Decimal(str(row[1] or 0))

    _merge_rows(db.execute(lamp_stmt).all())
    _merge_rows(db.execute(ac_stmt).all())
    return by_month
