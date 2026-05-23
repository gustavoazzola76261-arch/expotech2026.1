"""Respostas de erro (RFC 7807 Problem Details) e ações bem-sucedidas."""

from typing import Any

from pydantic import BaseModel, Field


class ProblemDetail(BaseModel):
    """application/problem+json — mensagem segura para o cliente."""

    type: str = Field(description="URI ou identificador do tipo de problema")
    title: str = Field(description="Resumo legível do status HTTP")
    status: int
    code: str = Field(description="Código estável da aplicação")
    detail: str = Field(description="Mensagem segura para exibição ao usuário")


class ActionResult(BaseModel):
    """Resposta padronizada para comandos (ligar/desligar em lote, etc.)."""

    message: str
    data: dict[str, Any] = Field(default_factory=dict)
