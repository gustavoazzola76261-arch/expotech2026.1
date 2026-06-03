from datetime import datetime

from pydantic import BaseModel, Field


class IAOperationContextRead(BaseModel):
    operation_context: str | None = None


class IAOperationContextUpdate(BaseModel):
    operation_context: str = Field(max_length=8000)


class IAInsightsResponse(BaseModel):
    analysis: str
    report: str
    savings_suggestions: list[str]
    waste_detection: list[str]
    model: str
    generated_at: datetime
    months_window: int
    room_id: int | None = None
    operation_context_used: str | None = None


class IALastReportResponse(BaseModel):
    has_report: bool
    generated_at: datetime | None = None
    months_window: int | None = None
    room_id: int | None = None
    model: str | None = None
    operation_context_used: str | None = None
    analysis: str | None = None
    report: str | None = None
    savings_suggestions: list[str] = Field(default_factory=list)
    waste_detection: list[str] = Field(default_factory=list)
