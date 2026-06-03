"""Monta contexto textual para o CrewAI a partir do banco."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import ActuationLog, Lamp, Room
from app.services.enel_tariff import energy_cost_brl, tariff_info


def _month_keys_between(start: datetime, end: datetime) -> list[str]:
    keys: list[str] = []
    cur = datetime(start.year, start.month, 1, tzinfo=start.tzinfo)
    end_m = datetime(end.year, end.month, 1, tzinfo=end.tzinfo)
    while cur <= end_m:
        keys.append(f"{cur.year:04d}-{cur.month:02d}")
        cur = cur + relativedelta(months=1)
    return keys


def build_energy_context(
    db: Session,
    months: int = 12,
    room_id: int | None = None,
    operation_context: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    first_this = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start = first_this if months == 1 else first_this - relativedelta(months=months - 1)

    if room_id is not None:
        lamp_filter = select(Lamp.id).where(Lamp.room_id == room_id)
        room = db.scalars(
            select(Room).where(Room.id == room_id).options(selectinload(Room.lamps))
        ).first()
        rooms = [room] if room else []
    else:
        lamp_filter = select(Lamp.id)
        rooms = list(
            db.scalars(select(Room).options(selectinload(Room.lamps)).order_by(Room.id)).unique().all()
        )

    bucket = func.date_trunc("month", ActuationLog.created_at)
    monthly_rows = db.execute(
        select(bucket, func.coalesce(func.sum(ActuationLog.energy_kwh), 0))
        .where(
            ActuationLog.energy_kwh.isnot(None),
            ActuationLog.created_at >= start,
            ActuationLog.created_at <= now,
            ActuationLog.lamp_id.in_(lamp_filter),
        )
        .group_by(bucket)
        .order_by(bucket)
    ).all()

    by_month: dict[str, Decimal] = {}
    for row in monthly_rows:
        b = row[0]
        if b is None:
            continue
        if b.tzinfo is None:
            b = b.replace(tzinfo=timezone.utc)
        by_month[f"{b.year:04d}-{b.month:02d}"] = Decimal(str(row[1] or 0))

    total_kwh = sum(by_month.values(), Decimal("0"))
    total_brl = energy_cost_brl(total_kwh)
    tariff = tariff_info()

    lines = [
        "=== Campus IoT — dados do sistema ===",
        f"Período analisado: {start.date()} a {now.date()} ({months} meses)",
        f"Filtro de sala: {room_id if room_id else 'todas'}",
        f"Consumo total no período: {total_kwh:.4f} kWh (R$ {total_brl:.2f})",
        f"Tarifa média Enel: R$ {tariff['unit_price_brl_per_kwh']}/kWh",
    ]

    if operation_context and operation_context.strip():
        lines.extend(["", "=== Contexto operacional do campus (informado pelo admin) ===", operation_context.strip()])

    lines.extend(["", "=== Consumo mensal (kWh | R$) ==="])
    for key in _month_keys_between(start, now):
        kwh = by_month.get(key, Decimal("0"))
        brl = energy_cost_brl(kwh)
        lines.append(f"  {key}: {kwh:.4f} kWh | R$ {brl:.2f}")

    lines.append("")
    lines.append("=== Consumo por sala (ranking, período completo) ===")
    room_rows = db.execute(
        select(
            Room.id,
            Room.name,
            Room.code,
            func.coalesce(func.sum(ActuationLog.energy_kwh), 0).label("kwh"),
        )
        .join(Lamp, Lamp.room_id == Room.id)
        .join(ActuationLog, ActuationLog.lamp_id == Lamp.id)
        .where(
            ActuationLog.energy_kwh.isnot(None),
            ActuationLog.created_at >= start,
            ActuationLog.created_at <= now,
            ActuationLog.lamp_id.in_(lamp_filter),
        )
        .group_by(Room.id, Room.name, Room.code)
        .order_by(func.coalesce(func.sum(ActuationLog.energy_kwh), 0).desc())
    ).all()
    if not room_rows:
        lines.append("  (sem consumo registrado por sala)")
    for row in room_rows:
        kwh = Decimal(str(row.kwh or 0))
        lines.append(f"  {row.name} ({row.code}): {kwh:.4f} kWh | R$ {energy_cost_brl(kwh):.2f}")

    lines.append("")
    lines.append("=== Consumo por hora do dia (ao desligar, fuso America/Sao_Paulo) ===")
    hour_col = func.extract("hour", ActuationLog.created_at)
    kwh_sum = func.coalesce(func.sum(ActuationLog.energy_kwh), 0)
    hour_rows = db.execute(
        select(
            hour_col.label("hr"),
            kwh_sum.label("kwh"),
            func.count(ActuationLog.id).label("events"),
        )
        .where(
            ActuationLog.energy_kwh.isnot(None),
            ActuationLog.created_at >= start,
            ActuationLog.created_at <= now,
            ActuationLog.lamp_id.in_(lamp_filter),
        )
        .group_by(hour_col)
        .order_by(kwh_sum.desc())
    ).all()
    if not hour_rows:
        lines.append("  (sem dados por hora)")
    else:
        for row in hour_rows:
            hr = int(row.hr) if row.hr is not None else -1
            kwh = Decimal(str(row.kwh or 0))
            lines.append(f"  {hr:02d}h: {kwh:.4f} kWh em {int(row.events)} desligamento(s)")

    lines.append("")
    lines.append("=== Estado atual das salas ===")
    for room in rooms:
        if room is None:
            continue
        lamps = sorted(room.lamps, key=lambda x: (x.slot, x.id)) if room.lamps else []
        on_count = sum(1 for lamp in lamps if lamp.is_on)
        lines.append(f"  Sala {room.id} — {room.name} ({room.code}): {on_count}/{len(lamps)} lâmpadas ligadas")

    lines.append("")
    lines.append("=== Amostra de desligamentos recentes (máx. 30) ===")
    logs = db.scalars(
        select(ActuationLog)
        .where(
            ActuationLog.energy_kwh.isnot(None),
            ActuationLog.lamp_id.in_(lamp_filter),
            ActuationLog.created_at >= start,
        )
        .options(joinedload(ActuationLog.lamp).joinedload(Lamp.room), joinedload(ActuationLog.user))
        .order_by(ActuationLog.created_at.desc())
        .limit(30)
    ).unique().all()
    if not logs:
        lines.append("  (sem registros)")
    for log in logs:
        lamp = log.lamp
        room_obj = lamp.room if lamp else None
        user = log.user.full_name if log.user else "sistema/agendamento"
        ts = log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "?"
        lines.append(
            f"  {ts} | {room_obj.name if room_obj else '?'} | "
            f"{float(log.energy_kwh or 0):.4f} kWh | {user}"
        )

    lamps_on = db.scalars(select(Lamp).where(Lamp.is_on.is_(True), Lamp.id.in_(lamp_filter))).all()
    if lamps_on:
        lines.append("")
        lines.append(f"=== Lâmpadas ligadas agora ({len(lamps_on)}) ===")
        for lamp in lamps_on:
            room_obj = db.get(Room, lamp.room_id)
            since = lamp.last_on_at.strftime("%Y-%m-%d %H:%M") if lamp.last_on_at else "?"
            lines.append(f"  {room_obj.name if room_obj else lamp.room_id} / {lamp.name} — desde {since}")

    return "\n".join(lines)
