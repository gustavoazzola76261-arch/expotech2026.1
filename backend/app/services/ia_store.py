from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.campus_ia_state import SINGLETON_ID, CampusIAState


def get_ia_state(db: Session) -> CampusIAState:
    row = db.get(CampusIAState, SINGLETON_ID)
    if row is None:
        row = CampusIAState(id=SINGLETON_ID)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def save_last_insights(db: Session, payload: dict[str, Any]) -> CampusIAState:
    row = get_ia_state(db)
    row.last_insights = payload
    row.last_generated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def set_operation_context(db: Session, text: str | None) -> CampusIAState:
    row = get_ia_state(db)
    row.operation_context = text.strip() if text and text.strip() else None
    db.commit()
    db.refresh(row)
    return row
