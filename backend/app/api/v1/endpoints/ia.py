import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.rate_limit import LIMIT_IA_INSIGHTS, limiter
from app.config import get_settings
from app.core.api_errors import internal_error, service_unavailable, validation
from app.database import get_db
from app.models import User, UserRole
from app.schemas.ia import (
    IAInsightsResponse,
    IALastReportResponse,
    IAOperationContextRead,
    IAOperationContextUpdate,
)
from app.services.ia_data import build_energy_context
from app.services.ia_store import get_ia_state, save_last_insights, set_operation_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ia", tags=["ia"])

_ALLOWED_WINDOWS = frozenset({1, 3, 6, 12})

_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _insights_from_stored(data: dict) -> IALastReportResponse:
    return IALastReportResponse(
        has_report=True,
        generated_at=datetime.fromisoformat(data["generated_at"])
        if isinstance(data.get("generated_at"), str)
        else data.get("generated_at"),
        months_window=data.get("months_window"),
        room_id=data.get("room_id"),
        model=data.get("model"),
        operation_context_used=data.get("operation_context_used"),
        analysis=data.get("analysis"),
        report=data.get("report"),
        savings_suggestions=data.get("savings_suggestions") or [],
        waste_detection=data.get("waste_detection") or [],
    )


@router.get("/operation-context", response_model=IAOperationContextRead)
def get_operation_context(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
) -> IAOperationContextRead:
    row = get_ia_state(db)
    return IAOperationContextRead(operation_context=row.operation_context)


@router.put("/operation-context", response_model=IAOperationContextRead)
def update_operation_context(
    payload: IAOperationContextUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
) -> IAOperationContextRead:
    row = set_operation_context(db, payload.operation_context)
    return IAOperationContextRead(operation_context=row.operation_context)


@router.get("/last-report", response_model=IALastReportResponse)
def get_last_report(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
) -> IALastReportResponse:
    row = get_ia_state(db)
    if not row.last_insights:
        return IALastReportResponse(has_report=False)
    return _insights_from_stored(row.last_insights)


@router.post("/insights", response_model=IAInsightsResponse)
@limiter.limit(LIMIT_IA_INSIGHTS)
async def generate_energy_insights(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
    months: int = Query(12, description="1, 3, 6 ou 12"),
    room_id: int | None = Query(default=None),
) -> IAInsightsResponse:
    if months not in _ALLOWED_WINDOWS:
        raise validation(public_key="months_invalid", log_detail=f"ia months={months}")

    settings = get_settings()
    if not settings.groq_api_key.strip():
        raise service_unavailable(public_key="ia_unavailable", log_detail="groq api key missing")

    ia_row = get_ia_state(db)
    op_ctx = ia_row.operation_context

    context = build_energy_context(db, months=months, room_id=room_id, operation_context=op_ctx)

    try:
        from IA.config import IASettings
        from IA.crew_energy import run_energy_insights

        ia_settings = IASettings(
            groq_api_key=settings.groq_api_key.strip(),
            groq_model=settings.groq_model,
            verbose=settings.ia_verbose,
        )
        result = await asyncio.to_thread(run_energy_insights, context, ia_settings)
    except ValueError as exc:
        raise service_unavailable(public_key="ia_unavailable", log_detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Falha ao executar CrewAI")
        raise internal_error(log_detail=str(exc)) from exc

    generated_at = datetime.now(timezone.utc)
    stored = {
        "analysis": result["analysis"],
        "report": result["report"],
        "savings_suggestions": result["savings_suggestions"],
        "waste_detection": result["waste_detection"],
        "model": result["model"],
        "generated_at": generated_at.isoformat(),
        "months_window": months,
        "room_id": room_id,
        "operation_context_used": op_ctx,
    }
    save_last_insights(db, stored)

    return IAInsightsResponse(
        analysis=result["analysis"],
        report=result["report"],
        savings_suggestions=result["savings_suggestions"],
        waste_detection=result["waste_detection"],
        model=result["model"],
        generated_at=generated_at,
        months_window=months,
        room_id=room_id,
        operation_context_used=op_ctx,
    )
