# ISSUE-41.3 — Reconciliação de estado documental (DIV-01..07, DIV-11)

## Contexto

A auditoria encontrou o estado documental descolado do código em uma dúzia de pontos, sendo o mais grave que `ESTADO_ATUAL.md` — declarado fonte de verdade que agentes leem a cada tarefa — desconhece a frente 40.x inteira. Esta issue é uma passada única de reconciliação, sem tocar código.

Origem: `docs/AUDITORIA_FABLE_2026-07.md` — DIV-01 a DIV-07, DIV-11, Melhoria-6 (TOP-4). DIV-08 já coberta pela 41.1; DIV-09 pela 41.2; DIV-10 sem ação (aceita); DIV-12 pela 33.3.

## Objetivo

Todo documento de estado/registro reflete o código real na data do merge, verificável pelos greps da própria auditoria.

## Fora de escopo

- Qualquer mudança de código, schema ou teste.
- Conteúdo editorial novo em framework/ além da linha de índice (DIV-04).

## Contrato / regras (uma por divergência)

| Código | Divergência | Ação |
|---|---|---|
| `RD_001` | DIV-01 | Seção "Fase — Sistema visual (40.1–40.6)" no `ROADMAP.md` com entregáveis reais; parágrafo correspondente no `ESTADO_ATUAL.md`. |
| `RD_002` | DIV-02 | `CLAUDE.md`: ponteiro de próxima issue atualizado (30.12 done; apontar para o estado real da fila no momento do merge). |
| `RD_003` | DIV-03 | Contagem de testes fixada **somente** em `ESTADO_ATUAL.md` (valor real de `pytest --collect-only -q` no dia); `CLAUDE.md` passa a referenciar "ver ESTADO_ATUAL" em vez de número próprio. |
| `RD_004` | DIV-04 | `framework/00_README.md`: linha do `20_SISTEMA_VISUAL.md` na tabela de ordem. |
| `RD_005` | DIV-05 | `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` registrado no `INDICE_DOCUMENTACAO.md`. |
| `RD_006` | DIV-06 | Roster único de casos no `ESTADO_ATUAL.md` incluindo `caso_gerado_cooperativa.json`; `showcase_tecnico.json` e `sinal_verde_demo_blueprint.json` classificados (demo/experimento) ou marcados para aposentadoria em issue futura — decisão registrada, não execução da aposentadoria. `AGENTS.md` alinhado ou apontando para o roster do ESTADO_ATUAL. |
| `RD_007` | DIV-07 | `GUIA_CODIGOS_ERROS.md`: decisão binária executada — (a) registrar as famílias RV/PV/FP/LS/CJ/SM (tabela resumida com link para módulo/spec de origem), ou (b) declarar explicitamente o escopo do guia (só validator) e onde vivem as demais famílias. Preferência da spec: (a), mantém o guia como registro central que o índice promete. |
| `RD_008` | DIV-11 | Issues 40.x: campo STATUS único e coerente (header contraditório removido); padrão documentado em uma linha no `ISSUE_TEMPLATE.md` se ainda não coberto. |
| `RD_009` | Melhoria-6 | Entrypoint do validator padronizado em `python -m generator.validator` em todos os docs e no CI (se o CI usar a forma de path, alinhar). |

## Impacto documental

Esta issue É o impacto documental: `ROADMAP.md`, `ESTADO_ATUAL.md`, `CLAUDE.md`, `AGENTS.md`, `framework/00_README.md`, `docs/INDICE_DOCUMENTACAO.md`, `docs/GUIA_CODIGOS_ERROS.md`, `.ai/issues/ISSUE-40.*.md`, `.ai/ISSUE_TEMPLATE.md`, possivelmente `.github/workflows/ci.yml` (RD_009).

## Casos de verificação (sem TDD de código)

1. `grep "40\." docs/ROADMAP.md docs/ESTADO_ATUAL.md` → seções presentes.
2. `pytest --collect-only -q | tail -1` → número bate com o ESTADO_ATUAL; `grep -n "138[0-9]\|146[0-9]" CLAUDE.md` → zero contagem fixada.
3. `grep "20_SISTEMA_VISUAL" framework/00_README.md` → presente.
4. `grep "EXPERIMENTO_GERACAO_DO_ZERO" docs/INDICE_DOCUMENTACAO.md` → presente.
5. `grep "cooperativa" docs/ESTADO_ATUAL.md` → roster presente.
6. `grep -c "RV_\|PV_\|FP_\|LS_\|CJ_\|SM_" docs/GUIA_CODIGOS_ERROS.md` → > 0 (se decisão (a)).
7. Headers das 40.x sem contradição (inspeção do revisor).
8. `pytest tests/ -q` sem regressão (prova de que nada de código foi tocado).

## Restrições arquiteturais

Documentação pura (exceto possível linha no ci.yml por RD_009). Nenhuma mutação de canônicos, código ou schemas.

## Critério de aceite

- [ ] `RD_001`–`RD_009` executadas, cada uma verificada pelo caso correspondente
- [ ] pytest tests/ -q sem regressão
- [ ] Revisor confirma por grep que nenhuma divergência da lista sobreviveu
