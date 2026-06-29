# ISSUE-30.7 — Estimador de dificuldade por profundidade, não por volume

## Contexto

Sondagem real (chamada direta a `generator/playtest_metrics.estimate_difficulty` com as entradas de produção `len(documentos)`, `count_required_contracts`, `infer_suspects`) revelou que o estimador **não distingue mais nível**: os quatro casos do roster estimam o mesmo valor.

```
caso                          docs  contr(req)  susp   estimada(atual)
Mirante     (decl. iniciante)   20      …          …    avancado
Iniciante B (decl. iniciante)    9      …          …    avancado
Aurora      (decl. intermediario)17     …          …    avancado
Fintech     (decl. avancado)    16      …          …    avancado
```

(Os valores exatos de `contr`/`susp` devem ser recapturados pela via de produção no STEP-01; o fato provado é que **todos os quatro estimam `avancado`**.) Confirmação independente pela via do validator: `PT_009` dispara no Mirante com `Declarada: iniciante; estimada: avancado`.

Causa-raiz, em `estimate_difficulty`:

```python
if documents > 30 or contracts > 12: return MESTRE
scores = [banda(documents), banda(contracts)]   # + banda(suspects) se houver
return DIFFICULTY_ORDER[max(scores)]
```

O modelo é puramente volumétrico e usa `max`: uma única contagem alta fixa o veredito. Como todos os canônicos têm contagens médias-altas de contratos e suspeitos, o `max` satura em `avancado` para todos. O estimador é, na prática, **degenerado** (saída constante no roster real).

Isso contradiz frontalmente um documento que já é fonte de verdade. `docs/DIFFICULTY_FRAMEWORK.md` afirma, textualmente:

> "Contagem de documentos não classifica dificuldade de forma confiável." … "Qualquer critério automatizado de dificuldade … deve tratar contagem de documentos e número de envelopes como **sinal informativo**, não como critério duro."

e enumera os sinais que **de fato** separam níveis: densidade de texto por documento; ambiguidade e cruzamentos simultâneos; findings de evidência (cadeias órfãs, suporte por conclusão); papel do E2 (confirmação simples vs. recontextualização forte vs. síntese entre documentos de naturezas diferentes).

**Origem:** auditoria de calibração 2026-06-28 (sondagem do estimador). Defeito alimenta o framework; não é patch de caso. Esta issue dá continuidade à linhagem de "métricas honestas" de ISSUE-30.6.

## Objetivo

`estimate_difficulty` passa a classificar por **profundidade dedutiva e densidade**, alinhado ao `DIFFICULTY_FRAMEWORK.md`, com contagem de documentos/suspeitos demovida a sinal informativo — de modo que o roster canônico volte a ser discriminado por nível.

## Fora de escopo

- **Não** recalibrar os tetos numéricos `DOCUMENT_RANGES`/`CONTRACT_LIMITS`/`SUSPECT_LIMITS` por nível (re-tuning de dados; pode virar follow-up). Esta issue troca o **classificador** e re-enquadra os avisos de contagem como informativos.
- **Não** mexer no Canonical Quality Gate (`canonical_quality_gate.py`) nem em `CANONICAL_CRITERIA` — o gate já foi endurecido em 30.6 e não consome `estimate_difficulty`.
- **Não** alterar blueprints canônicos. As dificuldades **declaradas** permanecem como estão (decisões editoriais); muda só a **estimativa automática** e o aviso de divergência.
- **Não** introduzir LLM nem dependência de rede; o sinal de profundidade vem do `clue_graph` já existente.

## Contrato / regras

`DIFFICULTY_ORDER = [iniciante, intermediario, avancado, especialista, mestre]`.

- **DF-01** — Novo classificador composto. `estimate_difficulty` deixa de ser função de contagens cruas e passa a derivar o nível de:
  1. **profundidade do caminho de solução** — `depth` do `clue_graph` (`_solution_path(...)["depth"]`, comprimento da cadeia de contratos obrigatórios até um contrato final), tomado como o `depth` máximo entre os contratos finais;
  2. **densidade por documento** — `densidade_total_chars / nº_documentos` (densidade total já é computada hoje como `sum(len(str(doc.conteudo)))`);
  3. **cruzamentos/ambiguidade** — proxy a partir do blueprint: nº de descartes (`descartes`), distribuição de `risco_ambiguidade` das evidências, e nº de red herrings (`infer_red_herrings`);
  4. **papel do E2** — sinal binário/ternário de recontextualização (há contrato obrigatório em E2 que reusa documento de E1? há salto que vira a leitura do E1?).
- **DF-02** — Contagem de documentos e de suspeitos entram **apenas como sinal informativo** (desempate suave), nunca como banda dominante via `max`. Nenhuma contagem isolada pode, sozinha, elevar o veredito mais de um nível acima do que profundidade+densidade indicam.
- **DF-03** — A assinatura pública de `estimate_difficulty` **pode** mudar para receber o `blueprint` (ou `graph_report`) em vez de três inteiros, já que precisa de profundidade/densidade. Atualizar o único chamador (`build_warnings`) de acordo. Manter retrocompatibilidade não é requisito; remover parâmetros mortos é preferível a mantê-los.
- **DF-04** — O caminho `documents > 30 or contracts > 12 → MESTRE` é substituído por um critério coerente com DF-01 (profundidade/densidade muito altas), não por contagem bruta.
- **DF-05** — `PT_009` (`_difficulty_warning`) passa a usar o novo estimador. Continua disparando só quando a distância entre declarada e estimada for ≥ 2 níveis (regra atual preservada).
- **DF-06** — Avisos `PT_001`/`PT_003`/`PT_007` (acima do recomendado por contagem) têm o **texto re-enquadrado** para deixar explícito que são *sinal informativo de carga de leitura*, não veredito de dificuldade (alinhando à frase do `DIFFICULTY_FRAMEWORK.md`). Severidade permanece `warning`; os tetos numéricos não mudam nesta issue.
- **DF-07** — O bloco `summary` retornado por `build_warnings` (`difficulty_estimated`, etc.) permanece com as mesmas chaves; só o **valor** de `difficulty_estimated` muda.

### Âncoras de regressão (contrato testável — o coração da issue)

| Caso | Arquivo | Declarada | Estimada exigida (pós-fix) |
|---|---|---|---|
| Iniciante B | `examples/caso_canonico_iniciante_b.json` | iniciante | **`iniciante`** (hoje: avancado) — âncora principal |
| Aurora | `examples/caso_canonico_intermediario.json` | intermediario | **`intermediario`** (hoje: avancado) |
| Fintech | `examples/caso_fintech.json` | avancado | **`avancado`** (hoje: avancado — travar p/ não regredir) |
| Mirante | `examples/caso_canonico_iniciante.json` | iniciante | **`!= avancado` e `<= intermediario`** |

> Sobre o Mirante: o `DIFFICULTY_FRAMEWORK.md` o trata como **exceção histórica** (Intermediário rebaixado a Iniciante, alto volume documental, baixa profundidade lógica) e manda **não usá-lo para calibrar limites métricos** — usar o Iniciante B. Coerente com o playtest ("fácil demais para Intermediário"), o estimador novo não pode rotulá-lo `avancado`. O teste exige `estimate(Mirante) ∈ {iniciante, intermediario}`, refletindo profundidade/densidade reais, não volume.

## Impacto documental
Consultar `docs/INDICE_DOCUMENTACAO.md` (gatilhos: "schema/validator/novos códigos" e a coluna "Atualizar quando" de `DIFFICULTY_FRAMEWORK.md` e `GUIA_CODIGOS_ERROS.md`).

- [ ] `docs/DIFFICULTY_FRAMEWORK.md` — fechar a divergência doc-vs-código: registrar que `estimate_difficulty` agora **implementa** o princípio "contagem é sinal, não classificador", citando os quatro sinais. Atualizar a tabela de métricas com a coluna "estimada (pós-fix)".
- [ ] `docs/GUIA_CODIGOS_ERROS.md` — atualizar a descrição de `PT_001`/`PT_003`/`PT_007` (re-enquadre informativo) e de `PT_009` (passa a usar estimador por profundidade).
- [ ] `framework/19_PLAYTEST_E_METRICAS.md` — descreve as métricas heurísticas; refletir o novo modelo de estimativa.
- [ ] `docs/ESTADO_ATUAL.md` — registrar, em "problemas já tratados", que o estimador de dificuldade era volumétrico e degenerado (constante no roster) e foi rebaseado em profundidade/densidade.
- [ ] `CLAUDE.md` — uma linha na nota de estado, se houver menção a métricas/dificuldade.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ⏭️ nenhum doc criado/movido; sem alteração esperada.

## Casos de teste (TDD — RED antes de GREEN)

Fixtures: os quatro blueprints canônicos já no repo. Os testes chamam a **via de produção** (derivar entradas como `build_warnings`/`estimate_difficulty` fazem hoje), em `tests/test_playtest_metrics.py`.

Novos (devem falhar antes da implementação):

1. `test_iniciante_b_estimated_iniciante` — Iniciante B → `iniciante`. (Hoje: avancado → RED.)
2. `test_aurora_estimated_intermediario` — Aurora → `intermediario`. (Hoje: avancado → RED.)
3. `test_fintech_estimated_avancado` — Fintech → `avancado`. (Hoje já passa; trava regressão.)
4. `test_mirante_not_estimated_avancado` — Mirante → `∈ {iniciante, intermediario}`. (Hoje: avancado → RED.)
5. `test_estimator_discriminates_roster` — o conjunto `{estimada(InicianteB), estimada(Aurora), estimada(Fintech)}` tem **pelo menos 3 valores distintos** ou cobre iniciante→avancado (prova de poder discriminativo; hoje é {avancado} → RED).
6. `test_document_count_does_not_dominate` — caso sintético com muitos documentos curtos e profundidade rasa estima ≤ `intermediario` (DF-02).
7. `test_pt009_uses_depth_estimator` — após o fix, `PT_009` **não** dispara para o Iniciante B nem para o Aurora (declarada bate com estimada dentro de 1 nível).

Atualizar (hoje codificam o comportamento volumétrico, se existirem):

- Qualquer teste existente que afirme `estimate_difficulty(...) == "avancado"` para Aurora/Iniciante B, ou que dependa da assinatura de três inteiros — revisar no STEP-01 e ajustar à nova assinatura/expectativa.

## Restrições arquiteturais

Herdar as padrão (`.ai/ISSUE_TEMPLATE.md`): sem LLM, sem rede, sem mutação de blueprints; sem duplicar dataclasses; `ruff` limpo; suíte sem regressão. **Reutilizar** `generator/clue_graph.py` para profundidade (`build_clue_graph` + `_solution_path`/`analyze_clue_graph`) — não reimplementar travessia de grafo. Densidade reusa o cálculo já existente; não duplicar.

## Critério de aceite

- [ ] DF-01..07 implementadas e cobertas por teste.
- [ ] Âncoras: Iniciante B→iniciante, Aurora→intermediario, Fintech→avancado, Mirante≠avancado — todas passam.
- [ ] O estimador discrimina o roster (teste 5).
- [ ] `PT_009` não dispara mais para Iniciante B/Aurora; texto de `PT_001/003/007` re-enquadrado.
- [ ] `pytest tests/ -q` sem regressão; `ruff` limpo nos arquivos tocados.
- [ ] `python -m generator.validator examples/caso_canonico_iniciante.json --strict` e nos demais canônicos roda sem novo erro (avisos podem mudar de texto).
- [ ] Impacto documental resolvido (cada item ✅ atualizado ou ⏭️ avaliado e não necessário).
