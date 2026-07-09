# ISSUE-32 — Fake Provider para testes determinísticos

## Contexto

A ISSUE-31 criou a interface `LLMProvider`. Para que os adapters LLM (ISSUE-33+) tenham CI determinística — sem rede, sem chave, sem flakiness — é preciso um provider falso que devolva respostas roteirizadas e permita injeção de falhas. Este é o mecanismo que preserva a restrição arquitetural "sem LLM nos testes" mesmo depois que código de produção passar a chamar modelos reais.

Origem: `docs/ROADMAP.md`, seção "ISSUE-32 — Fake Provider para testes".

## Objetivo

Existir `generator/fake_provider.py` com um `FakeProvider` que implementa `LLMProvider`, devolve respostas roteirizadas em ordem, registra os requests recebidos e injeta erros sob demanda.

## Fora de escopo

- Qualquer chamada de rede ou provider real.
- Alterar harness, pipeline ou solvers.
- Simulação de latência/streaming.

## Contrato / regras

Módulo novo: `generator/fake_provider.py`.

```python
@dataclass(frozen=True)
class ScriptedResponse:
    text: str
    model_id: str = "fake-model"

class FakeProvider:  # satisfaz LLMProvider (runtime_checkable)
    provider_id = "fake"
    def __init__(self, responses: Sequence[ScriptedResponse | ProviderError]): ...
    def complete(self, request: ProviderRequest) -> ProviderResponse: ...
    @property
    def calls(self) -> tuple[ProviderRequest, ...]: ...  # requests recebidos, em ordem
```

Regras nomeadas:

| Código | Condição | Efeito |
|---|---|---|
| `FP_001` | `complete` chamado com request inválido (`validate_provider_request` não vazio) | levanta `ProviderResponseError` com os erros PV na mensagem |
| `FP_002` | roteiro esgotado (mais chamadas que respostas) | levanta `ProviderResponseError("script exhausted")` |
| `FP_003` | item do roteiro é um `ProviderError` | a exceção é levantada naquela chamada (injeção de falha) |
| `FP_004` | resposta consumida | `ProviderResponse.request_id` ecoa o `request_id` do request |

Comportamento:

- Respostas são consumidas **em ordem**, uma por chamada — determinismo total.
- `calls` guarda cada request recebido (inclusive os que resultaram em erro injetado), permitindo asserções sobre o prompt montado pelo chamador.
- `FakeProvider` não muta os `ScriptedResponse` recebidos; `calls` é tupla (imutável para o consumidor).

## Impacto documental

- [ ] `docs/ROADMAP.md` — motivo: mover "ISSUE-32" para concluída.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: registrar o módulo e a garantia de CI determinística para a fase 33+.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ⏭️ provável: avaliar e justificar.

## Casos de teste (TDD)

Arquivo novo: `tests/test_fake_provider.py`.

1. `isinstance(FakeProvider([...]), LLMProvider)` é `True`.
2. Duas respostas roteirizadas são devolvidas na ordem exata do roteiro.
3. `FP_002`: terceira chamada com roteiro de duas respostas levanta `ProviderResponseError`.
4. `FP_003`: roteiro `[ScriptedResponse(...), ProviderTransportError("boom")]` — primeira chamada responde, segunda levanta a exceção injetada.
5. `FP_001`: request com prompt vazio levanta `ProviderResponseError` mencionando `PV_001`, sem consumir item do roteiro.
6. `FP_004`: `request_id="abc"` aparece ecoado na resposta.
7. `calls` registra todos os requests na ordem, incluindo o da chamada que recebeu erro injetado (mas não o rejeitado por FP_001 — request inválido não conta como consumo; registrar decisão no teste).

## Restrições arquiteturais

Herdar as padrão, sem exceções: sem LLM, sem rede, sem mutação, importar dataclasses da ISSUE-31 (proibido redeclarar), `ruff` limpo, `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `FP_001`–`FP_004` implementadas e cobertas por teste
- [ ] `FakeProvider` satisfaz o Protocol da ISSUE-31 sem herança nominal
- [ ] pytest tests/ -q passa sem regressão
- [ ] ruff limpo nos arquivos tocados
- [ ] impacto documental resolvido
