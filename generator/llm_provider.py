"""Contrato de provider LLM.

Este módulo define apenas a interface (Protocol) e as estruturas de dados
para requisições/respostas de um provider de LLM, mais validação de
requisição. NÃO chama nenhum LLM, NÃO acessa rede, NÃO implementa nenhum
provider real. É só o contrato que implementações futuras devem seguir.
"""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class ProviderRequest:
    """Requisição imutável para um provider de LLM."""

    prompt: str
    system: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.0
    request_id: str | None = None


@dataclass(frozen=True)
class ProviderResponse:
    """Resposta imutável de um provider de LLM."""

    text: str
    model_id: str
    request_id: str | None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None


@runtime_checkable
class LLMProvider(Protocol):
    """Interface que um provider de LLM real deve implementar."""

    provider_id: str

    def complete(self, request: ProviderRequest) -> ProviderResponse: ...


class ProviderError(RuntimeError):
    """Erro base de provider."""


class ProviderTransportError(ProviderError):
    """Erro de transporte/rede ao comunicar com o provider."""


class ProviderResponseError(ProviderError):
    """Erro de resposta inválida ou inesperada do provider."""


def validate_provider_request(request: ProviderRequest) -> list[str]:
    """Valida uma ProviderRequest sem mutá-la.

    Retorna lista de mensagens de erro (vazia se válida).
    """
    errors: list[str] = []

    if not request.prompt or not request.prompt.strip():
        errors.append("PV_001: prompt vazio ou só whitespace")

    if request.max_tokens <= 0:
        errors.append("PV_002: max_tokens deve ser maior que zero")

    if not (0.0 <= request.temperature <= 2.0):
        errors.append("PV_003: temperature fora do intervalo [0.0, 2.0]")

    if request.system is not None and not request.system.strip():
        errors.append("PV_004: system, quando fornecido, não pode ser vazio ou só whitespace")

    return errors
