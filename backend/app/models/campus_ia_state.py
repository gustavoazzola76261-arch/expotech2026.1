from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

SINGLETON_ID = 1


class CampusIAState(Base):
    """Configuração e último relatório IA (linha única id=1)."""

    __tablename__ = "campus_ia_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operation_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_insights: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    last_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
