# ISSUE-33.3 — Ligar o Conclusion Judge ao pipeline_runner (fim do gate fabricado)

## Contexto

`pipeline_runner._run_gate` fabrica `decision="approved"` e `met=True` incondicionalmente (`pipeline_runner.py:409`, `:635`, `:649`), mesmo quando um `LLMBlindSolver` real é injetado — o `judge_conclusions` (ISSUE-33.1) existe mas não tem chamador (AUDITORIA, RISCO-01/DIV-12). Um run com solver real produz manifest com aprovação que não reflete desempenho nenhum: exatamente o autoengano que o protocolo cego existe para impedir. Aproveita-se a mesma PR para o typo `EC-GUia-` (BUG-08), no mesmo arquivo.

Origem: `docs/AUDITORIA_FABLE_2026-07.md` — RISCO-01, DIV-12, BUG-08 (TOP-3).

## Objetivo

Quando um solver real e um provider são fornecidos ao pipeline, o gate passa a ser derivado do veredito real do `judge_conclusions`; sem provider, o comportamento stub atual é preservado byte a byte, mas honestamente documentado.

## Fora de escopo

- Alterar as regras do juiz (CJ_*) ou do gate (GE_*).
- Extração automática de conclusões esperadas do blueprint (continua responsabilidade do chamador/runner atual).
- Reviewers LLM (ISSUE-34).

## Contrato / regras

| Código | Regra |
|---|---|
| `PJ_001` | `run_pipeline`/`_run_gate` ganham caminho judge: com `judge_provider: LLMProvider | None = None` (novo parâmetro, default None), o runner chama `judge_conclusions(report, expected, judge_provider)` e mapeia o veredito para `ExpectedConclusion.met` reais. |
| `PJ_002` | `decision` derivada em Python puro do veredito + regras GE existentes: todos required met e sem flag de ambiguidade/vazamento → `approved`; caso contrário → `rejected` (com `gaps` preenchidos a partir das conclusões não met e da classificação CJ). Nunca confiada ao modelo. |
| `PJ_003` | `judge_provider=None` → comportamento atual preservado (gate fabricado do stub), zero regressão; o manifest passa a registrar `gate_mode: "stub" | "judged"` para eliminar ambiguidade de leitura. |
| `PJ_004` | Typo corrigido: `EC-GUia-` → `EC-GUIA-` (`pipeline_runner.py:646`). Verificar por grep que nenhum artefato versionado no repo referencia o id antigo; se referenciar, registrar decisão no report antes de mudar. |
| `PJ_005` | `judge_verdict` serializado é anexado ao workspace do run (artefato novo do pipeline), rastreável ao lado do run record. |

Nota de compatibilidade: `gate_mode` é campo novo em manifest — atualizar o schema correspondente mantendo `additionalProperties: false`; se manifests antigos são validados pelo schema novo em algum teste, o campo deve ser opcional com default implícito "stub" na leitura.

## Impacto documental

- [ ] `docs/ESTADO_ATUAL.md` — motivo: remover a lacuna enganosa (limitações passam a citar gate stub vs judged explicitamente).
- [ ] `docs/ROADMAP.md` — motivo: registrar 33.3; reescrever a frase "judge alimenta met" como fato (fecha DIV-12).
- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: seção do fluxo runner→judge→gate.
- [ ] `CLAUDE.md` — motivo: se citar limitação do gate, atualizar.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ✅/⏭️: avaliar.

## Casos de teste (TDD)

`tests/test_pipeline_runner.py` (estender) + fixtures das 33.x. FakeProvider sempre.

1. PJ_003 (regressão): pipeline sem `judge_provider` → manifests idênticos ao comportamento atual + `gate_mode="stub"`; testes existentes do pipeline continuam verdes.
2. PJ_001/002 caminho feliz: solver fake resolve, judge fake confirma todos met → `decision="approved"`, `gate_mode="judged"`, `met` vindos do veredito.
3. PJ_002 rejeição: judge fake nega um required → `decision="rejected"`, gap presente, GE_004 não viola (evaluation coerente).
4. PJ_002 ambiguidade: veredito com classificação `ambiguo` → `rejected` com gap correspondente.
5. PJ_005: artefato do veredito presente no workspace do run e válido contra `judge_verdict.schema.yaml`.
6. PJ_004: grep sem `EC-GUia` no repo pós-mudança; id novo nos manifests gerados.
7. Erro do judge (ProviderError nas duas tentativas) → falha do stage de gate com erro rastreável, não aprovação silenciosa.

## Restrições arquiteturais

Herdar as padrão + exceção declarada da fase (LLM só via provider injetado; testes offline). Derivação de decision em Python puro (PJ_002). Sem mutação de manifests existentes. `ruff` limpo; `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `PJ_001`–`PJ_005` implementadas e cobertas
- [ ] Caminho stub preservado byte a byte exceto `gate_mode` (regressão explícita)
- [ ] Falha do judge nunca vira aprovação silenciosa (caso 7)
- [ ] pytest tests/ -q sem regressão; ruff limpo
- [ ] impacto documental resolvido (DIV-12 fechada)
