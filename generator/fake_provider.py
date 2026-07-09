"""Fake LLM provider para testes determinísticos.

Implementa LLMProvider com respostas pré-roteirizadas, sem rede real.
Suporta injeção de falhas por ProviderError no roteiro.
"""

from dataclasses import dataclass
from typing import Sequence

from generator.llm_provider import (
    ProviderError,
    ProviderRequest,
    ProviderResponse,
    ProviderResponseError,
    validate_provider_request,
)


@dataclass(frozen=True)
class ScriptedResponse:
    """Resposta pré-roteirizada para o FakeProvider."""

    text: str
    model_id: str = "fake-model"


class FakeProvider:
    """Provider fake que satisfaz LLMProvider com respostas pré-roteirizadas.

    Comportamento:
    - Respostas consumidas em ordem, um índice interno por chamada válida.
    - FP_001: request inválido → levanta ProviderResponseError, não registra em calls.
    - FP_002: roteiro esgotado → levanta ProviderResponseError("script exhausted").
    - FP_003: item é ProviderError → levanta, mas registra em calls.
    - FP_004: ProviderResponse.request_id ecoa o request_id.
    """

    provider_id = "fake"

    def __init__(self, responses: Sequence[ScriptedResponse | ProviderError]):
        """Inicializa com roteiro de respostas/erros.

        Args:
            responses: sequência de ScriptedResponse ou ProviderError a consumir.
        """
        self._responses = responses
        self._index = 0
        self._calls: list[ProviderRequest] = []

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        """Completa uma requisição usando o roteiro pré-escrito.

        Implementa FP_001, FP_002, FP_003, FP_004.

        Args:
            request: ProviderRequest a processar.

        Returns:
            ProviderResponse com resposta do roteiro.

        Raises:
            ProviderResponseError: se request inválido (FP_001) ou roteiro esgotado (FP_002).
            ProviderError subclasses: se injetadas no roteiro (FP_003).
        """
        # FP_001: validar request antes de consumir do roteiro ou registrar em calls
        validation_errors = validate_provider_request(request)
        if validation_errors:
            error_message = "; ".join(validation_errors)
            raise ProviderResponseError(error_message)

        # FP_002: verificar se roteiro esgotado
        if self._index >= len(self._responses):
            raise ProviderResponseError("script exhausted")

        # Registrar request em calls (mesmo que vá resultar em erro injetado)
        self._calls.append(request)

        # Obter item do roteiro na posição atual
        current_response = self._responses[self._index]
        self._index += 1

        # FP_003: se é ProviderError, injetar (mas já registrou em calls acima)
        if isinstance(current_response, ProviderError):
            raise current_response

        # Caso normal: montar ProviderResponse
        # FP_004: request_id ecoa o request recebido
        return ProviderResponse(
            text=current_response.text,
            model_id=current_response.model_id,
            request_id=request.request_id,
        )

    @property
    def calls(self) -> tuple[ProviderRequest, ...]:
        """Retorna tupla imutável dos requests registrados."""
        return tuple(self._calls)
