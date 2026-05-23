"""Códigos e mensagens seguras da API (OWASP API Security — sem vazamento de detalhes internos)."""

from __future__ import annotations

import logging
from enum import StrEnum

logger = logging.getLogger(__name__)


class ErrorCode(StrEnum):
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION = "VALIDATION"
    BAD_REQUEST = "BAD_REQUEST"
    RATE_LIMITED = "RATE_LIMITED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# Mensagens públicas padrão por código HTTP / tipo de erro
DEFAULT_DETAIL: dict[ErrorCode, str] = {
    ErrorCode.UNAUTHORIZED: "Não foi possível autenticar.",
    ErrorCode.FORBIDDEN: "Você não tem permissão para esta ação.",
    ErrorCode.NOT_FOUND: "Recurso não encontrado.",
    ErrorCode.CONFLICT: "Não foi possível concluir a operação devido a um conflito.",
    ErrorCode.VALIDATION: "Os dados enviados são inválidos.",
    ErrorCode.BAD_REQUEST: "Requisição inválida.",
    ErrorCode.RATE_LIMITED: "Muitas requisições. Tente novamente em instantes.",
    ErrorCode.SERVICE_UNAVAILABLE: "Serviço temporariamente indisponível.",
    ErrorCode.INTERNAL_ERROR: "Erro interno. Tente novamente mais tarde.",
}

# Mensagens públicas específicas (sem IDs, caminhos, stack ou config interna)
PUBLIC_DETAIL: dict[str, str] = {
    "room_code_taken": "Este código de sala já está em uso.",
    "room_id_taken": "O identificador informado para a sala já está em uso.",
    "email_taken": "Este e-mail já está cadastrado.",
    "lamp_count_required": "Informe ao menos uma lâmpada.",
    "professor_needs_room": "Professor deve estar vinculado a ao menos uma sala.",
    "professor_room_ids": "Ao definir perfil professor, informe ao menos uma sala.",
    "room_ids_professor_only": "Salas vinculadas aplicam-se apenas ao perfil professor.",
    "months_invalid": "Período inválido. Use 1, 3, 6 ou 12 meses.",
    "schedule_not_found": "Programação não encontrada.",
    "schedule_target_invalid": "Destino da programação é inválido.",
    "schedule_rooms_required": "Selecione ao menos uma sala no grupo.",
    "schedule_lamps_required": "Selecione ao menos uma lâmpada no grupo.",
    "self_deactivate": "Você não pode desativar a própria conta.",
    "self_demote_admin": "Você não pode remover seu próprio perfil de administrador.",
    "ia_unavailable": "Análise por IA temporariamente indisponível.",
    "ac_temp_invalid": "Temperatura informada é inválida.",
    "device_credentials": "Credenciais do dispositivo inválidas.",
}


class APIError(Exception):
    """Exceção de API com mensagem pública segura e detalhe apenas para log."""

    def __init__(
        self,
        status_code: int,
        code: ErrorCode,
        *,
        public_detail: str | None = None,
        public_key: str | None = None,
        log_detail: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        if public_key is not None:
            self.detail = PUBLIC_DETAIL.get(public_key, DEFAULT_DETAIL[code])
        elif public_detail is not None:
            self.detail = public_detail
        else:
            self.detail = DEFAULT_DETAIL[code]
        self.log_detail = log_detail

    def log(self) -> None:
        if self.log_detail:
            logger.warning("[%s] %s", self.code, self.log_detail)


def unauthorized(*, log_detail: str | None = None) -> APIError:
    return APIError(401, ErrorCode.UNAUTHORIZED, log_detail=log_detail)


def forbidden(*, log_detail: str | None = None) -> APIError:
    return APIError(403, ErrorCode.FORBIDDEN, log_detail=log_detail)


def not_found(*, log_detail: str | None = None) -> APIError:
    return APIError(404, ErrorCode.NOT_FOUND, log_detail=log_detail)


def conflict(*, public_key: str | None = None, log_detail: str | None = None) -> APIError:
    return APIError(409, ErrorCode.CONFLICT, public_key=public_key, log_detail=log_detail)


def validation(*, public_key: str | None = None, log_detail: str | None = None) -> APIError:
    return APIError(422, ErrorCode.VALIDATION, public_key=public_key, log_detail=log_detail)


def bad_request(*, public_key: str | None = None, log_detail: str | None = None) -> APIError:
    return APIError(400, ErrorCode.BAD_REQUEST, public_key=public_key, log_detail=log_detail)


def service_unavailable(*, public_key: str | None = None, log_detail: str | None = None) -> APIError:
    return APIError(503, ErrorCode.SERVICE_UNAVAILABLE, public_key=public_key, log_detail=log_detail)


def internal_error(*, log_detail: str | None = None) -> APIError:
    return APIError(500, ErrorCode.INTERNAL_ERROR, log_detail=log_detail)
