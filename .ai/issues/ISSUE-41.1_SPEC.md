# ISSUE-41.1 — CI verde de novo: lint de tests/, symlinks no Windows e higiene de ambiente

## Contexto

CI está vermelha no `main` desde ≥ 2026-07-07: o step Lint (`ruff check generator/ scripts/ tests/`) falha com 55 erros em `tests/` (51× F811 por reimport de fixtures em `test_blind_solve_run_record.py`, 4× F401), abortando o workflow antes de `pytest` e dos validators — as ISSUE-33.2/40.5/40.6 entraram sem prova automatizada (AUDITORIA_FABLE_2026-07, BUG-01). Causa-raiz estrutural: o comando de lint obrigatório em `CLAUDE.md`/`AGENTS.md` cobre só `generator/` (RISCO-03/DIV-08). Além disso, 5 testes de symlink quebram no Windows sem skip-guard (BUG-02), normalizando suíte local vermelha; o CLI do validator emite mojibake em console cp1252 (Melhoria-4); e existe worktree órfão `.claude/worktrees/agent-adcf344320e399483/` (Melhoria-5).

Origem: `docs/AUDITORIA_FABLE_2026-07.md` — BUG-01, BUG-02, RISCO-03, DIV-08, Melhorias 1, 4, 5.

## Objetivo

`ruff check generator/ scripts/ tests/` limpo, `pytest tests/ -q` verde em Windows e Linux, CI verde no `main`, e comandos obrigatórios locais idênticos ao gate remoto.

## Fora de escopo

- Qualquer mudança de comportamento em código de produção (exceto o entrypoint de encoding do CLI).
- Reconciliação documental de estado (ISSUE-41.3).
- Alterar regras do ruff ou afrouxar o CI.

## Contrato / regras

| Código | Regra |
|---|---|
| `CI_001` | Fixtures compartilhadas de `tests/test_blind_solve_run_record.py` migram para `tests/conftest.py` (ou conftest local do diretório); nenhum `import` de fixture com `# noqa: F401` sobrevive em arquivos de teste. |
| `CI_002` | Zero F401 em `tests/` (remover os 4 imports não usados: `test_accessibility_reviewer.py:35`, `test_gate_font_fidelity.py:31`, `test_pipeline_runner.py:16`, `test_quality_comparative_reviewer.py:22`). |
| `CI_003` | Os 5 testes de symlink (generator/leak_checker/sanitizer) capturam `OSError` na criação do symlink e fazem `pytest.skip("symlinks not supported")`, seguindo o padrão de `tests/test_learning_ledger_cli.py:206`. O skip só cobre a criação do symlink — falha do código sob teste continua falhando. |
| `CI_004` | `CLAUDE.md` e `AGENTS.md` passam a exigir `ruff check generator/ scripts/ tests/` (idêntico ao CI). |
| `CI_005` | Entrypoint do CLI do validator força UTF-8 na saída (`sys.stdout.reconfigure(encoding="utf-8")` guardado por hasattr), eliminando mojibake em cp1252. |
| `CI_006` | Worktree órfão removido (`git worktree prune` + deleção do diretório); `.claude/worktrees/` adicionado ao `.gitignore` se ainda não coberto. |

## Impacto documental

- [ ] `CLAUDE.md` — motivo: CI_004 (comando de lint completo).
- [ ] `AGENTS.md` — motivo: CI_004.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: registrar CI restabelecida (uma linha).
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ⏭️ provável: avaliar e justificar.

## Casos de teste (TDD)

Esta issue é majoritariamente correção de testes/lint; o RED é o estado atual reproduzido:

1. RED: `ruff check tests/` registra os 55 erros atuais (evidência no report).
2. GREEN: `ruff check generator/ scripts/ tests/` → zero erros.
3. CI_001: `grep -rn "noqa: F401" tests/` → zero ocorrências em imports de fixture; suíte de `test_blind_solve_run_record.py` continua 100% verde (fixtures resolvidas via conftest).
4. CI_003: em ambiente sem privilégio de symlink os 5 testes reportam SKIP (não FAIL); em ambiente com symlink continuam a testar o comportamento real (verificar em CI Linux que eles executam, não skipam).
5. CI_005: teste unitário do entrypoint confirmando reconfigure chamado quando disponível (ou verificação manual documentada no report, se testar stdout global for frágil — decisão registrada).
6. `pytest tests/ -q` sem regressão nas duas plataformas (local Windows + CI Linux).

## Restrições arquiteturais

Herdar as padrão. Sem mudança de comportamento de produção além de CI_005. Proibido afrouxar regra de lint ou marcar teste como xfail para "passar".

## Critério de aceite

- [ ] `ruff check generator/ scripts/ tests/` limpo
- [ ] 5 testes de symlink com skip-guard correto (SKIP no Windows, EXEC no CI)
- [ ] CLAUDE.md/AGENTS.md alinhados ao comando do CI
- [ ] Run de CI verde no branch da PR (link no wrap-up)
- [ ] pytest tests/ -q sem regressão
- [ ] impacto documental resolvido
