from collections.abc import Callable
import secrets

from fastapi import Depends, Header, HTTPException, Query, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import get_settings
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
        description="Somente para testes no navegador/Swagger. A ESP32 deve usar o header X-Device-Key.",
    ),
) -> None:
    settings = get_settings()
    provided = _normalize_key(x_device_key) or _normalize_key(device_key)
    expected = _normalize_key(settings.esp32_device_key)

    if not provided:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Chave do dispositivo ausente. Envie o header X-Device-Key "
                "(ou query device_key=... apenas em testes)."
            ),
        )
    if not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Invalid device key. Confira ESP32_DEVICE_KEY em backend/.env "
                "(reinicie o uvicorn após alterar) e DEVICE_KEY no config.h da ESP."
            ),
        )


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from None
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user


def require_roles(*roles: UserRole) -> Callable[..., User]:
    def _inner(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _inner
