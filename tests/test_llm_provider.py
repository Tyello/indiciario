import dataclasses

import pytest

from generator.llm_provider import (
    LLMProvider,
    ProviderError,
    ProviderRequest,
    ProviderResponse,
    ProviderResponseError,
    ProviderTransportError,
    validate_provider_request,
)


def test_valid_request_has_no_errors():
    request = ProviderRequest(prompt="Olá, mundo")
    assert validate_provider_request(request) == []


@pytest.mark.parametrize("prompt", ["", "   "])
def test_pv001_empty_prompt(prompt):
    request = ProviderRequest(prompt=prompt)
    errors = validate_provider_request(request)
    assert any("PV_001" in e for e in errors)


@pytest.mark.parametrize("max_tokens", [0, -1])
def test_pv002_invalid_max_tokens(max_tokens):
    request = ProviderRequest(prompt="ok", max_tokens=max_tokens)
    errors = validate_provider_request(request)
    assert any("PV_002" in e for e in errors)


@pytest.mark.parametrize("temperature", [-0.1, 2.1])
def test_pv003_invalid_temperature(temperature):
    request = ProviderRequest(prompt="ok", temperature=temperature)
    errors = validate_provider_request(request)
    assert any("PV_003" in e for e in errors)


@pytest.mark.parametrize("temperature", [0.0, 2.0])
def test_pv003_valid_temperature_boundaries(temperature):
    request = ProviderRequest(prompt="ok", temperature=temperature)
    assert validate_provider_request(request) == []


def test_pv004_empty_system_string_errors():
    request = ProviderRequest(prompt="ok", system="")
    errors = validate_provider_request(request)
    assert any("PV_004" in e for e in errors)


def test_pv004_none_system_passes():
    request = ProviderRequest(prompt="ok", system=None)
    assert validate_provider_request(request) == []


def test_provider_request_is_frozen():
    request = ProviderRequest(prompt="ok")
    with pytest.raises(dataclasses.FrozenInstanceError):
        request.prompt = "outro"


def test_provider_response_is_frozen():
    response = ProviderResponse(text="ok", model_id="modelo-x", request_id=None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        response.text = "outro"


def test_llm_provider_protocol_runtime_checkable():
    class FakeProvider:
        provider_id = "fake"

        def complete(self, request):
            return ProviderResponse(text="ok", model_id="fake", request_id=None)

    class NotAProvider:
        provider_id = "not-a-provider"

    assert isinstance(FakeProvider(), LLMProvider)
    assert not isinstance(NotAProvider(), LLMProvider)


def test_error_hierarchy():
    assert issubclass(ProviderError, RuntimeError)
    assert issubclass(ProviderTransportError, ProviderError)
    assert issubclass(ProviderResponseError, ProviderError)
