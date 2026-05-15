import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.config import get_settings
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


app = FastAPI(title="Campus IoT API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Permite frontend em outras máquinas da rede (ex.: http://192.168.x.x:5173)
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
    return {"status": "ok"}


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "service": "Campus IoT API",
        "docs": "/docs",
        "health": "/health",
        "health_v1": "/api/v1/health",
    }
