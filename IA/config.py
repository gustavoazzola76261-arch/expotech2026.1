import os
from dataclasses import dataclass


@dataclass(frozen=True)
class IASettings:
    groq_api_key: str
    groq_model: str
    verbose: bool


def load_settings() -> IASettings:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    model = os.environ.get("GROQ_MODEL", "groq/llama-3.1-8b-instant").strip()
    verbose = os.environ.get("IA_VERBOSE", "false").lower() in ("1", "true", "yes")
    return IASettings(groq_api_key=key, groq_model=model, verbose=verbose)


def configure_groq_env(settings: IASettings | None = None) -> IASettings:
    cfg = settings or load_settings()
    if not cfg.groq_api_key:
        raise ValueError("GROQ_API_KEY não configurada. Defina no backend/.env ou IA/.env")
    os.environ["GROQ_API_KEY"] = cfg.groq_api_key
    return cfg
