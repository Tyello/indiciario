# ISSUE-31 — Provider Interface para LLM

## Contexto

O `pipeline_runner.py` usa um stub determinístico (`DeterministicPipelineSolver`) como blind solver — ninguém resolve o caso de fato (limitação conhecida registrada no `docs/ROADMAP.md`). Para conectar um modelo real (ISSUE-33) sem acoplar o pipeline a nenhum vendor, é preciso primeiro uma interface de provider neutra. Esta issue cria **somente a interface, os dataclasses e o contrato de erro** — nenhuma chamada de rede acontece aqui.

Origem: `docs/ROADMAP.md`, seção "ISSUE-31 — Provider Interface".

## Objetivo

Existir um módulo `generator/llm_provider.py` com um `Protocol` de provider, dataclasses imutáveis de request/response e hierarquia de erros, que qualquer adapter (fake, Anthropic, Ollama) possa implementar sem alterar consumidores.

## Fora de escopo

- Qualquer implementação concreta de provider (fake é ISSUE-32; real é config do usuário fora do repo).
- Qualquer chamada de rede, leitura de API key ou variável de ambiente.
- Alterar `pipeline_runner.py`, harness ou solvers existentes.
- Streaming, tool use, imagens — apenas completions de texto.

## Contrato / regras

Módulo novo: `generator/llm_provider.py`.

Dataclasses (todas `frozen=True`):

```python
@dataclass(frozen=True)
class ProviderRequest:
    prompt: str                      # prompt completo já montado pelo chamador
    system: str | None = None
    max_tokens: int = 4096           # > 0
    temperature: float = 0.0         # 0.0 <= t <= 2.0
    request_id: str | None = None    # correlação/auditoria

@dataclass(frozen=True)
class ProviderResponse:
    text: str
    model_id: str                    # identificação honesta do modelo que respondeu
    request_id: str | None
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None

@runtime_checkable
class LLMProvider(Protocol):
    provider_id: str
    def complete(self, request: ProviderRequest) -> ProviderResponse: ...
```

Hierarquia de erros:

- `ProviderError(RuntimeError)` — base.
- `ProviderTransportError(ProviderError)` — falha de rede/transporte (para adapters futuros).
- `ProviderResponseError(ProviderError)` — resposta malformada/vazia.

Regras nomeadas (validação em `validate_provider_request(request) -> list[str]`):

| Código | Condição | Efeito |
|---|---|---|
| `PV_001` | `prompt` vazio ou só whitespace | erro |
| `PV_002` | `max_tokens <= 0` | erro |
| `PV_003` | `temperature` fora de `[0.0, 2.0]` | erro |
| `PV_004` | `system` fornecido mas vazio/whitespace | erro |

`validate_provider_request` retorna lista de strings de erro (vazia quando válido), no mesmo estilo de `validate_run_record`. Não muta o request.

## Impacto documental

- [ ] `docs/ROADMAP.md` — motivo: mover "ISSUE-31" de pendente para concluída, com entregáveis.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: registrar o novo módulo e o início da fase Provider (31–34).
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ⏭️ provável: nenhum doc novo é criado; avaliar e justificar.

## Casos de teste (TDD)

Arquivo novo: `tests/test_llm_provider.py`.

RED antes de GREEN:

1. `ProviderRequest` válido passa `validate_provider_request` com lista vazia.
2. `PV_001`: prompt vazio e prompt `"   "` retornam erro com código na mensagem.
3. `PV_002`: `max_tokens=0` e `max_tokens=-1` retornam erro.
4. `PV_003`: `temperature=-0.1` e `temperature=2.1` retornam erro; `0.0` e `2.0` passam.
5. `PV_004`: `system=""` retorna erro; `system=None` passa.
6. Dataclasses são imutáveis: atribuição a campo levanta `FrozenInstanceError`.
7. Uma classe mínima de teste com `provider_id` e `complete` satisfaz `isinstance(obj, LLMProvider)` (runtime_checkable); uma sem `complete` não satisfaz.
8. Hierarquia: `ProviderTransportError` e `ProviderResponseError` são `ProviderError`; `ProviderError` é `RuntimeError`.

## Restrições arquiteturais

Herdar as padrão, sem exceções: **sem LLM, sem rede** (esta issue é só contrato), sem mutação de artefatos, sem duplicação de dataclasses (adapters futuros importam daqui), `ruff` limpo, `pytest tests/ -q` sem regressão. Nenhum schema YAML novo (contrato é Python puro, consumido internamente).

## Critério de aceite

- [ ] `PV_001`–`PV_004` implementadas e cobertas por teste
- [ ] Protocol `LLMProvider` runtime_checkable coberto por teste positivo e negativo
- [ ] pytest tests/ -q passa sem regressão
- [ ] ruff limpo nos arquivos tocados
- [ ] impacto documental resolvido (✅ atualizado ou ⏭️ avaliado e não necessário)
