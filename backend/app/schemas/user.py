from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole


class UserCreate(BaseModel):
    """Entrada para criação de usuário (admin)."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole
    password: str = Field(min_length=8, max_length=128)
    room_ids: list[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Atualização parcial (admin). Senha em branco / omitida = não altera."""

    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=1, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8, max_length=128)
    room_ids: list[int] | None = None


class UserRead(BaseModel):
    """Saída — e-mail como `str` para não falhar validação da resposta (ex.: dados legados no DB)."""

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UserReadAdmin(UserRead):
    room_ids: list[int] = Field(default_factory=list)
