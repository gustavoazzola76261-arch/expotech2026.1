from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, Field

from app.models.enums import UserRole
from app.schemas.validators import normalize_email


def _optional_email(value: Any) -> Any:
    if value is None:
        return None
    return normalize_email(str(value))


EmailField = Annotated[str, BeforeValidator(normalize_email)]
OptionalEmailField = Annotated[str | None, BeforeValidator(_optional_email)]


class UserCreate(BaseModel):
    """Entrada para criação de usuário (admin)."""

    email: EmailField
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole
    password: str = Field(min_length=8, max_length=128)
    room_ids: list[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Atualização parcial (admin). Senha em branco / omitida = não altera."""

    email: OptionalEmailField = None
    full_name: str | None = Field(None, min_length=1, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8, max_length=128)
    room_ids: list[int] | None = None


class UserRead(BaseModel):
    """Saída — e-mail como `str` para não falhar validação da resposta."""

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UserReadAdmin(UserRead):
    room_ids: list[int] = Field(default_factory=list)
