# ISSUE-33 — LLM Blind Solver Adapter

## Contexto

O harness cego (ISSUE-16) executa `solver.solve(context)` mas o único solver existente é o stub `DeterministicPipelineSolver` — limitação conhecida do `pipeline_runner.py`. Esta issue conecta um modelo real ao harness via `LLMProvider` (ISSUE-31), mantendo o **blind bundle como única entrada** do solver.

**Decisão de produto (registrada em chat):** o solver de produção usa Claude via API, injetado como provider. O solver **nunca** roda numa sessão de agente com acesso ao repositório, porque o repo contém o gabarito — isso violaria o protocolo cego. Nos testes, o provider é sempre o `FakeProvider` (ISSUE-32): CI determinística, sem rede.

Origem: `docs/ROADMAP.md`, seção "ISSUE-33 — LLM Blind Solver Adapter"; `docs/BLIND_SOLVER_HARNESS.md`.

## Objetivo

Existir `generator/llm_blind_solver.py` com um `LLMBlindSolver` que satisfaz o Protocol `BlindSolver`, monta o prompt exclusivamente a partir do `BlindSolverContext`, chama o provider injetado e converte a resposta em `BlindSolverReport` válido.

## Fora de escopo

- Adapter concreto para a API Anthropic (configuração do usuário, fora do repo nesta fase; o provider chega injetado).
- Julgar se a conclusão está correta (ISSUE-33.1).
- Múltiplas execuções / dificuldade (ISSUE-33.2).
- Alterar `pipeline_runner.py` para usar o novo solver por padrão (integração é passo explícito desta issue, mas o stub continua sendo o default sem provider).

## Contrato / regras

Módulo novo: `generator/llm_blind_solver.py`. Prompt versionado novo: `generator/prompts/blind_solver_v1.md` (PT-BR).

```python
class LLMBlindSolver:  # satisfaz BlindSolver (Protocol do harness)
    def __init__(self, provider: LLMProvider, prompt_version: str = "v1",
                 max_repair_attempts: int = 1): ...
    def solve(self, context: BlindSolverContext) -> BlindSolverReport: ...
```

### Montagem do prompt (regra de ouro do protocolo cego)

| Código | Condição | Efeito |
|---|---|---|
| `LS_001` | prompt contém qualquer conteúdo que não venha de: (a) template versionado, (b) artefatos lidos via `context.read_artifact_text`, (c) metadados do próprio context (`solver_run_id`, `solver_id`, lista de `included_artifacts`) | proibido por construção; teste de arquitetura verifica que o builder não recebe outros parâmetros |
| `LS_002` | resposta do provider não é JSON parseável ou não valida contra o schema do report | 1 tentativa de reparo (reenvio com erros anexados); persiste → `BlindSolverHarnessError` |
| `LS_003` | report produzido | `solver_run_id`, `solver_id`, `bundle_id`, `manifest_id` são sobrescritos a partir do context (nunca confiados ao modelo) |
| `LS_004` | resposta contém campos extras | descartados antes da validação (schema tem `additionalProperties: false`); descarte registrado em `warnings` do report |
| `LS_005` | template de prompt | carregado de `generator/prompts/blind_solver_v1.md`; hash sha256 do template registrado em `warnings` ou campo de auditoria do run (rastreabilidade de versão de prompt) |

### Template `blind_solver_v1.md` (conteúdo mínimo, PT-BR)

- Papel: detetive; única fonte de verdade são os artefatos fornecidos.
- Tarefa: identificar culpado, método e motivo **somente se** as evidências sustentarem; caso contrário, deixar `conclusion` vazia e registrar `open_questions`.
- Exigência: cada conclusão cita `artifact_id` + trecho/resumo em `evidence_used`.
- Exigência: se uma **solução alternativa** também satisfaz as evidências, declará-la em `open_questions` (insumo da ISSUE-33.1 para detectar ambiguidade).
- Formato: responder **somente** com JSON válido no schema do report (schema resumido embutido no template), sem markdown, sem preâmbulo.
- Proibição explícita de inventar artefatos não listados.

### Integração opt-in no pipeline

- `pipeline_runner.py` ganha parâmetro opcional `solver: BlindSolver | None = None`; `None` → mantém `DeterministicPipelineSolver` (comportamento atual preservado, zero regressão).

## Impacto documental

- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: nova seção "LLM Blind Solver Adapter (ISSUE-33)" com contrato LS_001–LS_005 e a regra de isolamento (solver nunca roda com acesso ao repo).
- [ ] `docs/ROADMAP.md` — motivo: mover ISSUE-33 para concluída; atualizar a limitação conhecida do stub.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: registrar o adapter e o caráter opt-in no pipeline.
- [ ] `docs/BLIND_CONTEXT_PROTOCOL.md` — motivo: registrar a decisão "solver de produção via API com bundle como única entrada; proibido em sessão com acesso ao repo".
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ⏭️ provável: avaliar (prompt versionado é código, não doc).

## Casos de teste (TDD)

Arquivo novo: `tests/test_llm_blind_solver.py`. Todos com `FakeProvider` sobre um bundle de fixture (reusar fixtures de bundle existentes de `tests/test_blind_solver_harness.py`).

1. Caminho feliz: FakeProvider devolve JSON válido → `solve` retorna `BlindSolverReport` que passa `validate_report`; ids sobrescritos do context (LS_003 — mesmo que o JSON traga ids errados).
2. LS_001 (arquitetura): o prompt registrado em `FakeProvider.calls[0].prompt` contém os textos dos artefatos do bundle e **não contém** nenhuma string sentinela plantada fora do bundle (ex.: conteúdo de um arquivo `gabarito_sentinela.txt` criado no tmp_path fora do bundle).
3. LS_002: primeira resposta é JSON inválido, segunda é válida → sucesso em 2 chamadas (repair); duas respostas inválidas → `BlindSolverHarnessError`.
4. LS_004: JSON com campo extra `chain_of_thought` → campo ausente do report final, warning registrado.
5. LS_005: hash do template presente no report/auditoria; alterar o template na fixture muda o hash.
6. Prompt inclui a lista exata de `included_artifacts` e nada além (comparação com manifest da fixture).
7. Integração: `run_blind_solver_harness` com `LLMBlindSolver(FakeProvider(...))` produz run record válido fim-a-fim.
8. Pipeline: `pipeline_runner` sem `solver` mantém comportamento atual (teste de regressão já existente continua verde); com solver injetado, o report do run vem do adapter.

## Restrições arquiteturais

Herdar as padrão, **com uma exceção declarada e justificada**: este módulo existe para chamar LLM em produção, mas (a) a chamada é sempre via `LLMProvider` injetado, (b) nenhum teste usa rede ou provider real, (c) nenhum default de provider real é instanciado no repo. Sem mutação de artefatos; sem duplicação de dataclasses (importa do harness e da ISSUE-31); `additionalProperties: false` já vigente no schema do report; `ruff` limpo; `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `LS_001`–`LS_005` implementadas e cobertas por teste
- [ ] Teste-sentinela do protocolo cego (caso 2) presente e verde
- [ ] Harness fim-a-fim com adapter + FakeProvider produz run record válido
- [ ] `pipeline_runner` sem provider preserva comportamento atual (zero regressão)
- [ ] pytest tests/ -q passa sem regressão
- [ ] ruff limpo nos arquivos tocados
- [ ] impacto documental resolvido
