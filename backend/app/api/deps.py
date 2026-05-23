from collections.abc import Callable
import secrets

from fastapi import Depends, Header, Query
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.api_errors import APIError, ErrorCode, forbidden, unauthorized
from app.core.security import decode_token
from app.database import get_db
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
device_key_header = APIKeyHeader(name="X-Device-Key", auto_error=False)


def _normalize_key(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().strip('"').strip("'")


def verify_esp32_device(
    x_device_key: str | None = Depends(device_key_header),
    device_key: str | None = Query(
        default=None,
        description="Somente para testes. A ESP32 deve usar o header X-Device-Key.",
    ),
) -> None:
    settings = get_settings()
    provided = _normalize_key(x_device_key) or _normalize_key(device_key)
    expected = _normalize_key(settings.esp32_device_key)

    if not provided:
        raise unauthorized(log_detail="device key missing")
    if not secrets.compare_digest(provided, expected):
        raise APIError(
            401,
            ErrorCode.UNAUTHORIZED,
            public_key="device_credentials",
            log_detail="device key mismatch",
        )


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise unauthorized(log_detail="jwt decode failed") from exc
    sub = payload.get("sub")
    if sub is None:
        raise unauthorized(log_detail="jwt missing sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as exc:
        raise unauthorized(log_detail="jwt invalid sub") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise unauthorized(log_detail=f"user inactive or missing id={user_id}")
    return user


def require_roles(*roles: UserRole) -> Callable[..., User]:
    def _inner(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise forbidden(log_detail=f"role {user.role} not in {roles}")
        return user

    return _inner
