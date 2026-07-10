# ISSUE-41.1 — Wrap-up

## Skill usada
spec-kit. Motivo: pedido explícito do usuário ("utilize o spec-kit"). Spec já existia pronta (ISSUE-41.1_SPEC.md) com contrato CI_001–CI_006 totalmente fechado (zero decisão residual) — classificação T2/T3, execução etapa a etapa seguindo o contrato, sem necessidade de nova clarificação.

## Arquivos alterados

- `tests/conftest.py` — fixtures `source_tree`, `output_root`, `browser` centralizadas (CI_001).
- `tests/test_blind_solver_harness.py` — fixtures locais removidas (movidas p/ conftest).
- `tests/test_blind_solve_run_record.py` — import de fixture com `noqa: F401` removido.
- `tests/test_font_vendoring.py` — fixture `browser` local removida, import `sync_playwright` removido.
- `tests/test_gate_font_fidelity.py` — import de `browser` e `typing.Any` não usado removidos (CI_001 + CI_002).
- `tests/test_accessibility_reviewer.py`, `tests/test_pipeline_runner.py`, `tests/test_quality_comparative_reviewer.py` — imports F401 não usados removidos via `ruff --fix` (CI_002).
- `tests/test_blind_bundle_generator.py`, `tests/test_blind_bundle_leak_checker.py` (3 sites), `tests/test_blind_bundle_sanitizer.py` — skip-guard `try/except (OSError, NotImplementedError): pytest.skip(...)` nos 5 testes de symlink (CI_003).
- `CLAUDE.md`, `AGENTS.md` — comando de lint obrigatório passa a `ruff check generator/ scripts/ tests/` (CI_004).
- `generator/validator.py` — `main()` força `sys.stdout.reconfigure(encoding="utf-8")` guardado por `hasattr` (CI_005).
- `tests/test_generator_validator.py` — `subprocess.run(..., encoding="utf-8")` no teste que lê stdout do CLI do validator, ajuste necessário decorrente direto de CI_005 (child agora sempre emite UTF-8; parent precisa decodificar como UTF-8 em vez de depender do locale do SO).
- `.gitignore` — `.claude/worktrees/` adicionado (CI_006).
- `docs/ESTADO_ATUAL.md` — uma linha registrando CI restabelecida (impacto documental).
- Worktree órfão `.claude/worktrees/agent-adcf344320e399483/` removido do disco e desregistrado do git (CI_006) — commit `5b6eb4e` confirmado ancestor de `main` antes da remoção (sem trabalho perdido).

## Decisão registrada (caso de teste 5 do contrato)

Teste unitário de `reconfigure` via `capsys`/mock de `sys.stdout` descartado por fragilidade (capture do pytest já substitui stdout, mascarando o comportamento real). Verificação manual feita: stub de stdout confirmou `reconfigure(encoding="utf-8")` é chamado quando o stream suporta o método, antes de qualquer `print`.

## Comandos executados e resultados

```
ruff check generator/ scripts/ tests/   → RED inicial: 55 erros (51 F811 [48 em test_blind_solve_run_record.py + 3 em test_gate_font_fidelity.py] + 4 F401)
ruff check generator/ scripts/ tests/   → GREEN final: All checks passed!
pytest tests/ -q                        → 1503 passed, 8 skipped (run limpo)
```

Nota sobre flake pré-existente: `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at` falha intermitentemente (~40% das execuções) tanto no `main` original quanto no branch desta issue — reproduzido isoladamente em 8 execuções na baseline sem nenhuma mudança (3 falhas de 8). Não é regressão desta entrega e está fora do contrato CI_001–CI_006 (bug de não-determinismo em `pipeline_runner.py`, produção). Não corrigido aqui — fora de escopo ("Sem mudança de comportamento de produção além de CI_005"). Recomendo issue própria.

5 testes de symlink: neste Windows sem privilégio de symlink, os 5 reportam SKIP (esperado). Comportamento em CI Linux (execução real, não skip) só verificável no run de CI da PR.

## Impacto documental resolvido

- ✅ `CLAUDE.md` — comando de lint atualizado (CI_004).
- ✅ `AGENTS.md` — comando de lint atualizado (CI_004).
- ✅ `docs/ESTADO_ATUAL.md` — uma linha registrando CI restabelecida.
- ⏭️ `docs/INDICE_DOCUMENTACAO.md` — avaliado, dispensado: nenhum doc novo ou movido; a mudança já cai no gatilho reverso existente "Contagem de testes, fase do pipeline, limitação conhecida" → `docs/ESTADO_ATUAL.md` + `CLAUDE.md`, ambos já resolvidos acima.

## Pendente (fora do meu controle local)

- [ ] Run de CI verde no branch da PR (link no wrap-up) — só confirmável após push/PR real.
