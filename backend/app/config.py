from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Sempre carrega backend/.env, mesmo se uvicorn for iniciado na raiz do repositório
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.is_file() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/campus_iot"
    secret_key: str = "dev-only-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"

    # Chave compartilhada com o firmware ESP32 (header X-Device-Key)
    esp32_device_key: str = "change-me-esp32-device-key"

    # Tarifa Enel SP (Grupo B convencional) — R$/kWh, ajuste conforme reajuste ANEEL
    enel_tariff_group: str = "B3 Convencional"
    enel_te_brl_per_kwh: Decimal = Decimal("0.41200")
    enel_tusd_brl_per_kwh: Decimal = Decimal("0.30900")
    enel_bandeira_brl_per_kwh: Decimal = Decimal("0.01874")
    enel_icms_rate: Decimal = Decimal("0.18")
    enel_pis_cofins_rate: Decimal = Decimal("0.0365")

    # CrewAI + Groq (pasta IA/ na raiz do repositório)
    groq_api_key: str = ""
    groq_model: str = "groq/llama-3.1-8b-instant"
    ia_verbose: bool = False
    campus_timezone: str = "America/Sao_Paulo"

    @field_validator("esp32_device_key", mode="before")
    @classmethod
    def normalize_device_key(cls, value: object) -> str:
        if value is None:
            return "change-me-esp32-device-key"
        text = str(value).strip().strip('"').strip("'")
        return text

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    """Útil após alterar .env — em dev, reinicie o uvicorn de qualquer forma."""
    get_settings.cache_clear()
