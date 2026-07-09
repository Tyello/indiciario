"""Testes para generator.fake_provider (ISSUE-32)."""

import pytest

from generator.fake_provider import FakeProvider, ScriptedResponse
from generator.llm_provider import (
    LLMProvider,
    ProviderRequest,
    ProviderResponseError,
    ProviderTransportError,
)


def test_fake_provider_is_instance_of_llm_provider():
    """Teste 1: FakeProvider satisfaz LLMProvider (runtime_checkable)."""
    provider = FakeProvider([ScriptedResponse("test")])
    assert isinstance(provider, LLMProvider)


def test_fake_provider_returns_responses_in_order():
    """Teste 2: Duas respostas roteirizadas são devolvidas na ordem exata."""
    responses = [
        ScriptedResponse("first response"),
        ScriptedResponse("second response", model_id="custom-model"),
    ]
    provider = FakeProvider(responses)

    req1 = ProviderRequest(prompt="prompt 1")
    resp1 = provider.complete(req1)
    assert resp1.text == "first response"
    assert resp1.model_id == "fake-model"

    req2 = ProviderRequest(prompt="prompt 2")
    resp2 = provider.complete(req2)
    assert resp2.text == "second response"
    assert resp2.model_id == "custom-model"


def test_fake_provider_fp_002_script_exhausted():
    """Teste 3: FP_002 — terceira chamada com roteiro de duas respostas levanta."""
    responses = [
        ScriptedResponse("first"),
        ScriptedResponse("second"),
    ]
    provider = FakeProvider(responses)

    provider.complete(ProviderRequest(prompt="prompt 1"))
    provider.complete(ProviderRequest(prompt="prompt 2"))

    # Terceira chamada deve esgotar o roteiro
    with pytest.raises(ProviderResponseError, match="script exhausted"):
        provider.complete(ProviderRequest(prompt="prompt 3"))


def test_fake_provider_fp_003_error_injection():
    """Teste 4: FP_003 — injeção de erro ProviderTransportError no roteiro."""
    responses = [
        ScriptedResponse("ok response"),
        ProviderTransportError("boom"),
    ]
    provider = FakeProvider(responses)

    # Primeira chamada: resposta normal
    req1 = ProviderRequest(prompt="prompt 1")
    resp1 = provider.complete(req1)
    assert resp1.text == "ok response"

    # Segunda chamada: erro injetado
    req2 = ProviderRequest(prompt="prompt 2")
    with pytest.raises(ProviderTransportError, match="boom"):
        provider.complete(req2)


def test_fake_provider_fp_001_invalid_request():
    """Teste 5: FP_001 — request com prompt vazio levanta PV_001."""
    responses = [ScriptedResponse("never consumed")]
    provider = FakeProvider(responses)

    # Request com prompt vazio
    invalid_request = ProviderRequest(prompt="")

    with pytest.raises(ProviderResponseError, match="PV_001"):
        provider.complete(invalid_request)

    # Request inválido não consome do roteiro e não é registrado em calls
    assert len(provider.calls) == 0


def test_fake_provider_fp_004_request_id_echo():
    """Teste 6: FP_004 — request_id é ecoado na resposta."""
    responses = [ScriptedResponse("response")]
    provider = FakeProvider(responses)

    req = ProviderRequest(prompt="test", request_id="abc")
    resp = provider.complete(req)

    assert resp.request_id == "abc"


def test_fake_provider_calls_includes_error_injection_but_not_invalid():
    """Teste 7: calls registra válidos (incluindo que resultaram em erro), não invalidos."""
    responses = [
        ScriptedResponse("ok"),
        ProviderTransportError("injected"),
        ScriptedResponse("ok2"),
    ]
    provider = FakeProvider(responses)

    # Chamada 1: válida, sucesso
    req1 = ProviderRequest(prompt="p1", request_id="id1")
    provider.complete(req1)

    # Chamada 2: válida, mas resultado é erro injetado
    req2 = ProviderRequest(prompt="p2", request_id="id2")
    with pytest.raises(ProviderTransportError):
        provider.complete(req2)

    # Chamada 3: inválida, deve levantar sem registrar
    req3_invalid = ProviderRequest(prompt="")
    with pytest.raises(ProviderResponseError, match="PV_001"):
        provider.complete(req3_invalid)

    # Chamada 4: válida, sucesso
    req4 = ProviderRequest(prompt="p4", request_id="id4")
    provider.complete(req4)

    # calls deve ter req1, req2, req4 (não req3_invalid porque foi rejeitado)
    assert len(provider.calls) == 3
    assert provider.calls[0].request_id == "id1"
    assert provider.calls[1].request_id == "id2"
    assert provider.calls[2].request_id == "id4"

    # Confirmar que calls é tupla (imutável para consumidor)
    assert isinstance(provider.calls, tuple)
