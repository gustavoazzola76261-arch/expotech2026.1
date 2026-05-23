from datetime import datetime, timezone
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.api_errors import validation
from app.database import get_db
from app.models import User, UserRole
from app.schemas.consumption import (
    ConsumptionMonthlyPoint,
    ConsumptionMonthlyResponse,
    ConsumptionSummary,
    EnelTariffInfo,
)
from app.services.enel_tariff import energy_cost_brl, tariff_info
from app.services.energy import monthly_energy_by_key, sum_total_energy_kwh

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
    total_kwh = sum_total_energy_kwh(db, room_id=room_id)
    return ConsumptionSummary(
        total_kwh=total_kwh,
        total_brl=energy_cost_brl(total_kwh),
        tariff=EnelTariffInfo(**tariff_info()),
    )


@router.get("/monthly", response_model=ConsumptionMonthlyResponse)
def consumption_monthly(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
    months: int = Query(12, description="1 = mês atual; 3, 6 ou 12 = últimos N meses (incluindo o atual)"),
    room_id: int | None = Query(default=None, description="Filtrar por sala (opcional)"),
) -> ConsumptionMonthlyResponse:
    if months not in _ALLOWED_WINDOWS:
        raise validation(public_key="months_invalid", log_detail=f"months={months}")

    now = datetime.now(timezone.utc)
    start = _window_start(months, now)
    by_month = monthly_energy_by_key(db, start=start, end=now, room_id=room_id)

    keys = _month_keys_between(start, now)
    points = []
    for k in keys:
        kwh = by_month.get(k, Decimal("0"))
        points.append(
            ConsumptionMonthlyPoint(
                year_month=k,
                kwh=kwh,
                brl=energy_cost_brl(kwh),
            )
        )
    total_kwh = sum((p.kwh for p in points), Decimal("0"))
    total_brl = sum((p.brl for p in points), Decimal("0"))

    return ConsumptionMonthlyResponse(
        months_window=months,
        period_start=start,
        period_end=now,
        points=points,
        total_kwh_in_period=total_kwh,
        total_brl_in_period=total_brl,
        tariff=EnelTariffInfo(**tariff_info()),
    )
