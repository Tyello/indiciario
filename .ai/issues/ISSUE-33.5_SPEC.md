# ISSUE-33.5 — Reprodutibilidade e temperatura real no Solvability Meter

## Contexto

O parâmetro `temperature` do meter é validado e depois morto: não vai ao report (schema não tem campo) nem ao `ProviderRequest` (solver e judge hardcodam 0.0) — com provider determinístico, N runs degeneram para o mesmo resultado e o meter mede quase nada (BUG-06); a premissa da ISSUE-33.2 ("N execuções **com temperatura**") não está implementada. Além disso o `SolvabilityReport` não registra setup (prompt-hashes, provider) e existe colisão de nome público `estimate_difficulty` entre `playtest_metrics.py` e `solvability_meter.py` com semânticas diferentes (Melhorias 2 e 3).

Origem: `docs/AUDITORIA_FABLE_2026-07.md` — BUG-06, Melhorias 2 e 3.

## Objetivo

O meter repassa `temperature` de fato ao solver, registra o setup completo de reprodutibilidade no report, e a colisão de nomes é desfeita.

## Fora de escopo

- Mudar limiares SM_003 ou lógica de flags.
- Repassar temperatura ao judge (juiz permanece a 0.0 — julgamento deve ser determinístico; decisão registrada em doc).

## Contrato / regras

| Código | Regra |
|---|---|
| `RM_001` | `measure_solvability` repassa `temperature` ao `ProviderRequest` de cada run do **solver** (via parâmetro novo em `LLMBlindSolver.solve`/construtor, decisão de plumbing no STEP-01); judge permanece `temperature=0.0`, documentado. |
| `RM_002` | `SolvabilityReport` ganha bloco `reproducibility`: `temperature`, `provider_id`, `solver_prompt_sha256`, `judge_prompt_sha256`, `runs_requested`. Schema atualizado mantendo `additionalProperties: false`. |
| `RM_003` | `solvability_meter.estimate_difficulty` renomeado para `estimate_difficulty_from_solve_rate`; `playtest_metrics.estimate_difficulty` intocado. Sem alias de compatibilidade (busca por chamadores no STEP-01; repo é a única base de consumo). |
| `RM_004` | Runs continuam usando o mesmo bundle e mesmo prompt (SM_002 preservado); a única variação intencional entre runs é a temperatura/semente do provider. |

## Impacto documental

- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: bloco reproducibility + decisão "judge sempre 0.0".
- [ ] `framework/19_PLAYTEST_E_METRICAS.md` — motivo: nota de que a estimativa agora varia com temperatura (proxy calibrável).
- [ ] `docs/ESTADO_ATUAL.md` — motivo: uma linha.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ✅/⏭️: avaliar.

## Casos de teste (TDD)

1. RM_001: `measure_solvability(..., temperature=0.7)` → cada `ProviderRequest` do solver em `FakeProvider.calls` tem `temperature=0.7`; requests do judge têm `0.0`.
2. RM_002: report serializado contém bloco `reproducibility` completo e valida contra o schema atualizado; hash muda quando o template de prompt da fixture muda.
3. RM_003: `from generator.solvability_meter import estimate_difficulty` falha; `estimate_difficulty_from_solve_rate` cobre a tabela de limiares existente (testes atuais migrados).
4. RM_004: asserção de que o prompt do solver é idêntico entre runs (exceto nada — mesmo texto), com temperaturas iguais entre si.
5. Regressão: casos existentes do meter (SM_001–005) continuam verdes após rename e schema novo.

## Restrições arquiteturais

Herdar as padrão + exceção declarada da fase. `additionalProperties: false` preservado. Sem quebra de SM_002. `ruff` limpo; `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `RM_001`–`RM_004` implementadas e cobertas
- [ ] Temperatura comprovadamente chega ao provider do solver e não ao do judge
- [ ] pytest tests/ -q sem regressão; ruff limpo
- [ ] impacto documental resolvido
