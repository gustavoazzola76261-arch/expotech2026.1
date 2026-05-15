from fastapi import APIRouter

from app.api.v1.endpoints import actuations, admin_users, auth, consumption, ia, iot, lamps, me, rooms, schedules

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(me.router)
api_router.include_router(rooms.router)
api_router.include_router(lamps.router)
api_router.include_router(consumption.router)
api_router.include_router(admin_users.router)
api_router.include_router(actuations.router)
api_router.include_router(iot.router)
api_router.include_router(schedules.router)
api_router.include_router(ia.router)
