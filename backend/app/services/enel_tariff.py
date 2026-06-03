"""
Custo estimado em R$ com base na composição tarifária Enel (Grupo B — convencional).

Referência: estrutura da fatura (TE + TUSD + bandeira + tributos), conforme
ANEEL/Enel — https://www.enel.com.br/pt-saopaulo/Corporativo_e_Governo/geracao-distribuida/estrutura-da-fatura-de-energia.html

Valores unitários (R$/kWh) são configuráveis em .env para acompanhar reajustes homologados.
"""

from decimal import Decimal, ROUND_HALF_UP

from app.config import Settings, get_settings

_MONEY = Decimal("0.01")


def tariff_info(settings: Settings | None = None) -> dict[str, str]:
    s = settings or get_settings()
    unit = unit_price_brl_per_kwh(s)
    return {
        "distributor": "Enel SP",
        "tariff_group": s.enel_tariff_group,
        "te_brl_per_kwh": str(s.enel_te_brl_per_kwh),
        "tusd_brl_per_kwh": str(s.enel_tusd_brl_per_kwh),
        "bandeira_brl_per_kwh": str(s.enel_bandeira_brl_per_kwh),
        "icms_rate": str(s.enel_icms_rate),
        "pis_cofins_rate": str(s.enel_pis_cofins_rate),
        "unit_price_brl_per_kwh": str(unit),
    }


def unit_price_brl_per_kwh(settings: Settings | None = None) -> Decimal:
    """Preço médio R$/kWh com tributos (ICMS por dentro + PIS/COFINS)."""
    s = settings or get_settings()
    base = s.enel_te_brl_per_kwh + s.enel_tusd_brl_per_kwh + s.enel_bandeira_brl_per_kwh
    if base <= 0:
        return Decimal("0")
    # ICMS "por dentro" e PIS/COFINS sobre a parcela de energia (modelo simplificado oficial)
    with_pis = base / (Decimal("1") - s.enel_pis_cofins_rate)
    with_icms = with_pis / (Decimal("1") - s.enel_icms_rate)
    return with_icms.quantize(_MONEY, rounding=ROUND_HALF_UP)


def energy_cost_brl(kwh: Decimal, settings: Settings | None = None) -> Decimal:
    if kwh <= 0:
        return Decimal("0")
    unit = unit_price_brl_per_kwh(settings)
    return (kwh * unit).quantize(_MONEY, rounding=ROUND_HALF_UP)
