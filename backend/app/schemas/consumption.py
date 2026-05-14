from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import LampAction


class ActuationRead(BaseModel):
    id: int
    created_at: datetime
    lamp_id: int
    action: LampAction
    energy_kwh: Decimal | None

    model_config = {"from_attributes": True}


class ConsumptionSummary(BaseModel):
    total_kwh: Decimal
    period_start: datetime | None = None
    period_end: datetime | None = None


class ConsumptionMonthlyPoint(BaseModel):
    """Um mês no gráfico (sempre YYYY-MM)."""

    year_month: str = Field(examples=["2026-01"])
    kwh: Decimal


class ConsumptionMonthlyResponse(BaseModel):
    months_window: int = Field(description="Janela solicitada: 1, 3, 6 ou 12")
    period_start: datetime
    period_end: datetime
    points: list[ConsumptionMonthlyPoint]
    total_kwh_in_period: Decimal
