# ISSUE-33.6 — Evidência citada ⊆ evidência lida (auditabilidade do run cego)

## Contexto

`_validate_report_semantics` do harness valida que `evidence_used.artifact_id` existe no bundle, mas não cruza com `context.accessed_artifacts` — um solver pode citar artefato que nunca abriu, "chutando" citações plausíveis pelos metadados listados no prompt (AUDITORIA, RISCO-02). Hoje é teórico (o `LLMBlindSolver` lê tudo para montar o prompt), mas vira real com solvers de leitura seletiva — e o log de acessos existe exatamente para essa auditoria.

Origem: `docs/AUDITORIA_FABLE_2026-07.md` — RISCO-02, EVO ISSUE-33.6.

## Objetivo

O harness sinaliza, com código de validação próprio, toda citação de evidência cujo artefato não consta no log de acessos do round.

## Fora de escopo

- Mudar o comportamento do `LLMBlindSolver` (que continua lendo tudo).
- Transformar o warning em erro fatal (decisão futura, quando existir solver seletivo).

## Contrato / regras

| Código | Regra |
|---|---|
| `RV_009` | Novo código na família do `blind_solver_report_validator`/harness: `evidence_used` cita `artifact_id` ∉ `accessed_artifacts` do round → **warning** estruturado no resultado do harness (`citacao_sem_leitura`), listando os ids ofensores. Não bloqueia o run. |
| `RV_010` | O warning é registrado também no run record (campo/lista de warnings existente), garantindo trilha auditável fora da memória do processo. |
| `RV_011` | Zero falso positivo no caminho atual: run do `LLMBlindSolver` (que acessa todos os artefatos) nunca dispara RV_009 — teste de regressão explícito. |

Numeração RV_009+ deve ser confirmada no STEP-01 contra o validador real (se RV_009 já existir, usar o próximo livre e atualizar a SPEC no report).

## Impacto documental

- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: documentar RV_009/010 na seção de validação semântica.
- [ ] `docs/GUIA_CODIGOS_ERROS.md` — ✅/⏭️: conforme decisão da ISSUE-41.3 sobre onde vivem as famílias RV; justificar.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: uma linha.

## Casos de teste (TDD)

1. Solver fake que responde citando artefato incluído no bundle mas **nunca lido** (report montado manualmente, sem passar por leitura) → resultado do harness contém warning `citacao_sem_leitura` com o id exato.
2. RV_010: o mesmo warning presente no run record serializado e válido contra o schema do run record.
3. RV_011: run integração com `LLMBlindSolver` + FakeProvider → zero warnings dessa família.
4. Citação de artefato lido + citação de não-lido no mesmo report → warning lista só o não-lido.

## Restrições arquiteturais

Herdar as padrão. Warning, não erro (não muda decisão de nenhum gate). Sem mudança de schema além de reutilizar canais de warning existentes; se o schema do run record não comportar, registrar e estender mantendo `additionalProperties: false`. `ruff` limpo; `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `RV_009`–`RV_011` implementadas e cobertas
- [ ] Zero falso positivo no fluxo atual (caso 3)
- [ ] pytest tests/ -q sem regressão; ruff limpo
- [ ] impacto documental resolvido
