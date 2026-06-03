"""Rate limiting (SlowAPI) — contagem por IP do cliente (memória local).

Rotas com @limiter.limit precisam declarar `request: Request` e `response: Response`
(FastAPI injeta a Response vazia para o SlowAPI gravar X-RateLimit / Retry-After).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Limites padrão da API (rotas sem decorator específico, via SlowAPIMiddleware)
LIMIT_DEFAULT = "120/minute"

# Rotas sensíveis
LIMIT_LOGIN = "10/minute"
LIMIT_IA_INSIGHTS = "5/minute"
LIMIT_IOT_POLL = "180/minute"
LIMIT_DEVICE_COMMAND = "60/minute"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[LIMIT_DEFAULT],
    headers_enabled=True,
)
