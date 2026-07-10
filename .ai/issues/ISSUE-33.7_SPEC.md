# ISSUE-33.7 — created_at real quebra determinismo de narrative/evidence review

## Contexto

`generator/narrative_reviewer.review_narrative` (`narrative_reviewer.py:385`) e
`generator/evidence_reviewer.review_evidence` (`evidence_reviewer.py:332`) gravam
`created_at=_now_iso()` — relógio real do processo — em vez de aceitar um `created_at`
explícito. `pipeline_runner._run_reviews` (`pipeline_runner.py:545-566`) chama as duas
funções sem repassar o `created_at` fixo que `run_pipeline` recebe e usa para o resto do
manifest. Resultado: `test_run_pipeline_is_deterministic_with_same_created_at`
(`tests/test_pipeline_runner.py`) é intermitente — quando as duas chamadas do teste
cruzam a fronteira de segundo, o `created_at` embutido no `narrative_review`/
`evidence_review` diverge, o sha256 do artefato diverge, e o teste falha mesmo com
`created_at` fixo passado a `run_pipeline`. Reproduzido 2x em rodadas completas de
`pytest tests/ -q` durante a execução de ISSUE-33.3; não reproduz isolado (3/3 passa
sozinho) porque as duas chamadas então caem dentro do mesmo segundo.

Origem: achado durante validação (STEP-06) de ISSUE-33.3, registrado como dívida em
`.ai/runs/ISSUE-33.3/STEP-06_EXECUTION.md`. Não é regressão de ISSUE-33.3 (arquivos não
tocados por aquela issue).

## Objetivo

`run_pipeline` produz manifest byte a byte idêntico entre duas execuções com o mesmo
`created_at`, incluindo os artefatos `narrative_review` e `evidence_review`.

## Fora de escopo

- Mudar regras NR_*/ER_* ou o conteúdo dos findings.
- Qualquer outro consumidor de `review_narrative`/`review_evidence` fora de
  `pipeline_runner.py` (nenhum outro encontrado no STEP-01; confirmar).

## Contrato / regras

| Código | Regra |
|---|---|
| `NC_001` | `review_narrative`/`review_evidence` ganham parâmetro `created_at: str \| None = None`; quando fornecido, é usado literalmente no `ReviewReport`; quando `None`, comportamento atual (`_now_iso()`) é preservado — zero regressão para chamadores existentes fora do pipeline. |
| `NC_002` | `pipeline_runner._run_reviews` passa a receber e repassar o `created_at` do run (mesmo valor usado no resto do manifest) às duas chamadas. |
| `NC_003` | `test_run_pipeline_is_deterministic_with_same_created_at` deixa de ser intermitente: rodar em loop (ex. 20x) sem falha atribuível a timestamp de narrative/evidence review. |

## Impacto documental

- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: seção do pipeline runner já documenta o fluxo de gate/artefatos; registrar que `created_at` do run agora é propagado aos reviewers.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: remover a limitação de determinismo intermitente, se citada; uma linha.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ✅/⏭️: avaliar.

Se nenhum doc precisar mudar além dos listados, justificar no report.

## Casos de teste (TDD)

1. NC_001: `review_narrative(..., created_at="2026-01-01T00:00:00Z")` → `ReviewReport.created_at == "2026-01-01T00:00:00Z"`; sem o argumento, comportamento atual (`_now_iso()`) preservado (teste de regressão explícito, congelando `_now_iso` ou usando janela de tolerância).
2. Idêntico para `review_evidence`.
3. NC_002: `run_pipeline` chamado duas vezes com o mesmo `created_at` → `narrative_review`/`evidence_review` (e seus sha256 em `artifacts_summary`) idênticos entre as duas chamadas.
4. NC_003: `test_run_pipeline_is_deterministic_with_same_created_at` rodado em loop (ex. `pytest -q --count=20` ou laço manual no teste) sem falha.
5. Regressão: suíte completa de `tests/test_narrative_reviewer.py`/`tests/test_evidence_reviewer.py` continua verde.

## Restrições arquiteturais

Herdar as padrão. Sem mutação de assinatura obrigatória para chamadores existentes fora do
pipeline (parâmetro novo é opcional, default preserva comportamento). `ruff` limpo;
`pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `NC_001`–`NC_003` implementadas e cobertas
- [ ] `test_run_pipeline_is_deterministic_with_same_created_at` deixa de ser intermitente (caso 4)
- [ ] pytest tests/ -q sem regressão; ruff limpo
- [ ] impacto documental resolvido
