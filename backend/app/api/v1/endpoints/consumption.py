from datetime import datetime, timezone
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database import get_db
from app.models import ActuationLog, Lamp, User, UserRole
from app.schemas.consumption import ConsumptionMonthlyPoint, ConsumptionMonthlyResponse, ConsumptionSummary

router = APIRouter(prefix="/consumption", tags=["consumption"])

_ALLOWED_WINDOWS = frozenset({1, 3, 6, 12})


def _window_start(months: int, now: datetime) -> datetime:
    first_this = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if months == 1:
        return first_this
    return first_this - relativedelta(months=months - 1)


def _month_keys_between(start: datetime, end: datetime) -> list[str]:
    keys: list[str] = []
    cur = datetime(start.year, start.month, 1, tzinfo=start.tzinfo)
    end_m = datetime(end.year, end.month, 1, tzinfo=end.tzinfo)
    while cur <= end_m:
        keys.append(f"{cur.year:04d}-{cur.month:02d}")
        cur = cur + relativedelta(months=1)
    return keys


@router.get("/summary", response_model=ConsumptionSummary)
def consumption_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
    room_id: int | None = Query(default=None),
) -> ConsumptionSummary:
    if room_id is not None:
        lamp_ids_subq = select(Lamp.id).where(Lamp.room_id == room_id)
    else:
        lamp_ids_subq = select(Lamp.id)

    stmt = select(func.coalesce(func.sum(ActuationLog.energy_kwh), 0)).where(
        ActuationLog.energy_kwh.isnot(None),
        ActuationLog.lamp_id.in_(lamp_ids_subq),
    )
    total = db.scalar(stmt)
    return ConsumptionSummary(total_kwh=Decimal(str(total or 0)))


@router.get("/monthly", response_model=ConsumptionMonthlyResponse)
def consumption_monthly(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
    months: int = Query(12, description="1 = mês atual; 3, 6 ou 12 = últimos N meses (incluindo o atual)"),
    room_id: int | None = Query(default=None, description="Filtrar por sala (opcional)"),
) -> ConsumptionMonthlyResponse:
    if months not in _ALLOWED_WINDOWS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="months deve ser 1, 3, 6 ou 12",
        )

    now = datetime.now(timezone.utc)
    start = _window_start(months, now)

    if room_id is not None:
        lamp_ids_subq = select(Lamp.id).where(Lamp.room_id == room_id)
    else:
        lamp_ids_subq = select(Lamp.id)

    bucket = func.date_trunc("month", ActuationLog.created_at)
    stmt = (
        select(bucket, func.coalesce(func.sum(ActuationLog.energy_kwh), 0))
        .where(
            ActuationLog.energy_kwh.isnot(None),
            ActuationLog.created_at >= start,
            ActuationLog.created_at <= now,
            ActuationLog.lamp_id.in_(lamp_ids_subq),
        )
        .group_by(bucket)
        .order_by(bucket)
    )
    rows = db.execute(stmt).all()

    by_month: dict[str, Decimal] = {}
    for row in rows:
        b = row[0]
        if b is None:
            continue
        if b.tzinfo is None:
            b = b.replace(tzinfo=timezone.utc)
        key = f"{b.year:04d}-{b.month:02d}"
        by_month[key] = Decimal(str(row[1] or 0))

    keys = _month_keys_between(start, now)
    points = [ConsumptionMonthlyPoint(year_month=k, kwh=by_month.get(k, Decimal("0"))) for k in keys]
    total_period = sum((p.kwh for p in points), Decimal("0"))

    return ConsumptionMonthlyResponse(
        months_window=months,
        period_start=start,
        period_end=now,
        points=points,
        total_kwh_in_period=total_period,
    )
