from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware.logging_middleware import (LoggingMiddleware)
from app.core.middleware.security_middleware import (SecurityMiddleware)
from app.core.middleware.rate_limit_middleware import (RateLimitMiddleware)
from app.core.exceptions.handlers import (
    app_exception_handler,
    generic_exception_handler
)
from app.core.exceptions.custom_exceptions import (AppException)

from app.api.v1.routers import (
    auth_router,
    users_router,
    rooms_router,
    lamps_router,
    devices_router,
    energy_router,
    iot_router
)

from app.core.middleware.logging_middleware import LoggingMiddleware

app = FastAPI(
    title="Smart Campus API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#exception handlers
app.add_exception_handler(
    AppException,
    app_exception_handler
)

app.add_exception_handler(
    Exception,
    generic_exception_handler
)

# Routers
app.include_router(auth_router.router, prefix="/api/v1/auth")
app.include_router(users_router.router, prefix="/api/v1/users")
app.include_router(rooms_router.router, prefix="/api/v1/rooms")
app.include_router(lamps_router.router, prefix="/api/v1/lamps")
app.include_router(devices_router.router, prefix="/api/v1/devices")
app.include_router(energy_router.router, prefix="/api/v1/energy")
app.include_router(iot_router.router, prefix="/api/v1/iot")

@app.get("/")
async def root():
    return {
        "message": "Smart Campus API Running"
    }