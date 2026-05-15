from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import LampAction


class ActuationHistoryRead(BaseModel):
    id: int
    created_at: datetime
    action: LampAction
    energy_kwh: Decimal | None
    user_id: int | None
    user_name: str | None
    user_email: str | None
    room_id: int
    room_name: str
    room_code: str
    lamp_id: int
    lamp_name: str
    lamp_slot: int
