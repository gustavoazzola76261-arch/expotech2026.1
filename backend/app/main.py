import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.exception_handlers import (
    api_error_handler,
    http_exception_handler,
    rate_limit_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.api.v1.router import api_router
from app.config import get_settings
from app.core.api_errors import APIError
from app.rate_limit import limiter
from app.services.scheduler import run_due_schedules

logger = logging.getLogger(__name__)
settings = get_settings()

_scheduler_task: asyncio.Task | None = None


async def _scheduler_loop() -> None:
    while True:
        await asyncio.to_thread(run_due_schedules)
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler_task
    _scheduler_task = asyncio.create_task(_scheduler_loop())
    logger.info("Agendador de programações iniciado (verificação a cada 30s)")
    yield
    if _scheduler_task:
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Campus IoT API",
    version="1.0.0",
    lifespan=lifespan,
    responses={
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão"},
        404: {"description": "Recurso não encontrado"},
        422: {"description": "Dados inválidos"},
        429: {"description": "Limite de requisições"},
        500: {"description": "Erro interno"},
    },
)
app.state.limiter = limiter
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

_LAN_ORIGIN_REGEX = (
    r"https?://"
    r"(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(:\d+)?"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=_LAN_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["meta"])
@app.get("/api/v1/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "message": "Serviço em execução."}


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "service": "Campus IoT API",
        "message": "API em execução. Consulte a documentação em /docs.",
        "docs": "/docs",
        "health": "/health",
    }
