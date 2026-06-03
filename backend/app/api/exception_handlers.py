"""Handlers globais: erros sanitizados (OWASP) e log detalhado apenas no servidor."""

from __future__ import annotations

import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.core.api_errors import APIError, DEFAULT_DETAIL, ErrorCode

logger = logging.getLogger(__name__)

PROBLEM_CONTENT_TYPE = "application/problem+json"

_STATUS_TITLES: dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
}


def _problem_type(code: str) -> str:
    return f"urn:campus-iot:error:{code.lower()}"


def problem_response(
    *,
    status: int,
    code: str,
    detail: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = {
        "type": _problem_type(code),
        "title": _STATUS_TITLES.get(status, "Error"),
        "status": status,
        "code": code,
        "detail": detail,
    }
    return JSONResponse(status_code=status, content=body, media_type=PROBLEM_CONTENT_TYPE, headers=headers)


def _map_http_exception(exc: HTTPException) -> tuple[int, str, str]:
    """Converte HTTPException legado em mensagem segura; registra o detail original."""
    status = exc.status_code
    original = exc.detail
    if isinstance(original, list):
        log_detail = str(original)
    else:
        log_detail = str(original) if original is not None else ""

    if log_detail:
        logger.warning("HTTPException %s: %s", status, log_detail)

    code_map: dict[int, ErrorCode] = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
        422: ErrorCode.VALIDATION,
        429: ErrorCode.RATE_LIMITED,
        500: ErrorCode.INTERNAL_ERROR,
        502: ErrorCode.INTERNAL_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }
    err_code = code_map.get(status, ErrorCode.INTERNAL_ERROR)
    safe_detail = DEFAULT_DETAIL[err_code]
    return status, err_code.value, safe_detail


async def api_error_handler(_request: Request, exc: APIError) -> JSONResponse:
    exc.log()
    headers = {}
    if exc.status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"
    return problem_response(
        status=exc.status_code,
        code=exc.code.value,
        detail=exc.detail,
        headers=headers or None,
    )


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    status, code, detail = _map_http_exception(exc)
    headers = dict(exc.headers) if exc.headers else {}
    if status == 401 and "WWW-Authenticate" not in headers:
        headers["WWW-Authenticate"] = "Bearer"
    return problem_response(status=status, code=code, detail=detail, headers=headers or None)


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Validação rejeitada: %s", exc.errors())
    return problem_response(
        status=HTTP_422_UNPROCESSABLE_ENTITY,
        code=ErrorCode.VALIDATION.value,
        detail=DEFAULT_DETAIL[ErrorCode.VALIDATION],
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Erro não tratado: %s", exc)
    return problem_response(
        status=500,
        code=ErrorCode.INTERNAL_ERROR.value,
        detail=DEFAULT_DETAIL[ErrorCode.INTERNAL_ERROR],
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    logger.warning("Rate limit: %s", request.url.path)
    response = problem_response(
        status=429,
        code=ErrorCode.RATE_LIMITED.value,
        detail=DEFAULT_DETAIL[ErrorCode.RATE_LIMITED],
    )
    limiter = getattr(request.app.state, "limiter", None)
    view_limit = getattr(request.state, "view_rate_limit", None)
    if limiter is not None and view_limit is not None:
        return limiter._inject_headers(response, view_limit)
    return response
