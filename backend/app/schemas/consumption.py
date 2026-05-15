from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class EnelTariffInfo(BaseModel):
    distributor: str
    tariff_group: str
    te_brl_per_kwh: str
    tusd_brl_per_kwh: str
    bandeira_brl_per_kwh: str
    icms_rate: str
    pis_cofins_rate: str
    unit_price_brl_per_kwh: str


class ConsumptionSummary(BaseModel):
    total_kwh: Decimal
    total_brl: Decimal
    tariff: EnelTariffInfo


class ConsumptionMonthlyPoint(BaseModel):
    """Um mês no gráfico (sempre YYYY-MM)."""

    year_month: str = Field(examples=["2026-01"])
    kwh: Decimal
    brl: Decimal


class ConsumptionMonthlyResponse(BaseModel):
    months_window: int = Field(description="Janela solicitada: 1, 3, 6 ou 12")
    period_start: datetime
    period_end: datetime
    points: list[ConsumptionMonthlyPoint]
    total_kwh_in_period: Decimal
    total_brl_in_period: Decimal
    tariff: EnelTariffInfo
