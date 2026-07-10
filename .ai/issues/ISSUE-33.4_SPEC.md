# ISSUE-33.4 — Hardening do adapter LLM e do judge (respostas hostis do modelo)

## Contexto

A auditoria encontrou quatro defeitos de robustez no `llm_blind_solver.py` e um no `conclusion_judge.py` que um modelo real vai acionar em produção: JSON não-objeto ou `warnings` não-lista → `AttributeError` cru (BUG-03); item de `evidence_used` com campo extra → `TypeError` cru (BUG-04); `max_repair_attempts=N` executa no máximo 1 reparo (BUG-05); placeholders de id substituídos depois do conteúdo dos artefatos, permitindo injeção mínima via bundle (BUG-07); e o `JudgeVerdict` final não é revalidado contra o schema, podendo violar `minLength` com defaults (RISCO-04). Como o Solvability Meter só captura a família de erros contratual, exceções cruas matam a medição inteira em vez de degradar para run incompleta.

Origem: `docs/AUDITORIA_FABLE_2026-07.md` — BUG-03/04/05/07, RISCO-04 (TOP-5).

## Objetivo

Toda resposta malformada do provider resulta em reparo ou em erro da família contratual (`BlindSolverHarnessError`/`ConclusionJudgeError`) — nunca `AttributeError`/`TypeError` crus — e o veredito final do judge é garantidamente schema-válido.

## Fora de escopo

- Mudar prompts ou schemas de report/veredito (exceto se RISCO-04 exigir default conforme).
- Ligar judge ao pipeline (ISSUE-33.3).
- Metadados de reprodutibilidade (ISSUE-33.5).

## Contrato / regras

| Código | Regra |
|---|---|
| `HD_001` | Pós-parse do solver: `isinstance(result, dict)` obrigatório; não-dict entra no fluxo de reparo e, esgotado, `BlindSolverHarnessError`. `warnings` não-lista é normalizado para lista de str com warning registrado. (fecha BUG-03) |
| `HD_002` | Cada item de `evidence_used`: se não-dict → reparo/erro contratual; se dict com campos extras → filtrado por `fields(BlindSolverEvidence)` com warning (mesmo tratamento LS_004 do nível raiz). (fecha BUG-04) |
| `HD_003` | Loop real de reparo: até `max_repair_attempts` reenvios com erros anexados, seguindo o padrão já correto do `conclusion_judge.py`; teste com N=2 exige 3 chamadas ao provider antes do erro. (fecha BUG-05) |
| `HD_004` | Ordem de substituição no builder de prompt: ids/metadados primeiro, conteúdo de artefatos por último; conteúdo de artefato contendo o literal `{bundle_id}` permanece literal no prompt. (fecha BUG-07) |
| `HD_005` | `JudgeVerdict` final serializado e revalidado contra `judge_verdict.schema.yaml` antes do retorno; defaults gerados (`verdict_id`, `report_run_id`) garantidamente conformes (`minLength`), com fallback documentado quando o report não traz run id. (fecha RISCO-04) |

## Impacto documental

- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: registrar HD_001–HD_005 nas seções do adapter e do judge.
- [ ] `docs/GUIA_CODIGOS_ERROS.md` — ⏭️ provável nesta issue: famílias serão reconciliadas na ISSUE-41.3; avaliar e justificar para não duplicar trabalho.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: uma linha.

## Casos de teste (TDD)

`tests/test_llm_blind_solver.py` e `tests/test_conclusion_judge.py` (estender). FakeProvider sempre.

1. HD_001: fake devolve `[1,2,3]` válido em JSON → reparo disparado; duas respostas não-dict → `BlindSolverHarnessError` (não `AttributeError`).
2. HD_001: `"warnings": "nenhum"` → report final com warnings lista, aviso de normalização presente.
3. HD_002: evidência com `"page": 2` extra → campo filtrado + warning; evidência `"string solta"` → reparo/erro contratual (não `TypeError`).
4. HD_003: `max_repair_attempts=2` com 3 respostas inválidas → exatamente 3 chamadas registradas em `FakeProvider.calls` e erro contratual; com resposta válida na 3ª → sucesso.
5. HD_004: artefato de fixture contendo o literal `{bundle_id}` → prompt final contém o literal, não o valor real (inverte o cenário do BUG-07).
6. HD_005: report sem `solver_run_id`/`run_id` → veredito ainda schema-válido (fallback conforme); veredito final sempre revalidado (teste com monkeypatch quebrando um default deve falhar na revalidação, não retornar silenciosamente).
7. Integração com o meter: run cujo solver devolve JSON não-objeto conta como run incompleta (`RUNS_INCOMPLETAS`), não derruba `measure_solvability`.

## Restrições arquiteturais

Herdar as padrão + exceção declarada da fase. Sem mudança de contrato público (assinaturas preservadas; `max_repair_attempts` passa a honrar a semântica já documentada). `ruff` limpo; `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `HD_001`–`HD_005` implementadas e cobertas
- [ ] Nenhum caminho de resposta malformada produz exceção fora da família contratual (caso 7 prova na integração)
- [ ] pytest tests/ -q sem regressão; ruff limpo
- [ ] impacto documental resolvido
