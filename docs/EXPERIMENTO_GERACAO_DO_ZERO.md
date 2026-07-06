# Experimento — Geração-do-zero (ISSUE-30.11)

**Status:** faixa (a) — métricas de pipeline — preenchida (STEP-04). Faixa (b) — rubrica humana — pendente de playtest (STEP-05). Não canônico. Não é régua.

Este documento registra o experimento que responde: conseguimos gerar um caso **novo**
(não transcrito) no nível do corpus de calibração externo (`examples/caso_referencia_uma_noite_sem_flores.json`,
ISSUE-30.8/30.10)? Pipeline-verde é necessário, não suficiente — o veredito é o playtest humano (HUMAN-01).

Ver `.ai/issues/ISSUE-30.11.md` e `.ai/issues/ISSUE-30.11_SPEC.md` para contrato completo.

---

## 1. Parâmetros do caso gerado

| Parâmetro | Valor |
|---|---|
| Domínio | **Cooperativa agrícola** — desvio de carga de grãos (soja) numa cooperativa rural |
| Motivo da escolha | Distinto de museu/arte (domínio do corpus de calibração) e distinto dos domínios já usados nos canônicos (hotel × 2, biblioteca, plantão hospitalar, fintech). Domínio fresco: silo, balança de pesagem, logística de caminhões, cota de armazenagem — dá superfície natural para presença física + credencial + cadeia logística, sem se apoiar em nada do corpus transcrito. |
| Dificuldade declarada | Intermediário |
| Envelopes | 2 |
| Arquivo de saída (STEP-02) | `examples/caso_gerado_cooperativa.json` |
| Marcação obrigatória | `observacoes_producao` deve declarar `experimental, não-canônico, gerado do zero para ISSUE-30.11` |

### Padrões PAT a empregar deliberadamente (≥ 2, GEN-03)

Intenção nesta fase (STEP-01); a declaração real e rastreável no blueprint acontece no STEP-02.

| PAT | Como deve aparecer no domínio cooperativa |
|---|---|
| **PAT-01 — Pilar de presença (credencial × regra)** | Log de acesso ao pátio/silo (crachá + catraca) só vira prova de presença cruzado com o manual/regulamento interno que declara a catraca de uso pessoal e intransferível. |
| **PAT-04 — Virada de envelope (suspeito presente / objeto ausente)** | E1 identifica quem tinha acesso ao pátio no horário do carregamento. E2 vira a pergunta: a carga que saiu no caminhão não bate com a nota fiscal — "quem" não basta, o caso passa a perseguir "para onde foi a carga". |

Candidatos adicionais a considerar no STEP-02, se couberem sem forçar a narrativa:
- **PAT-02 — Descarte por motivo-sem-oportunidade**: um operador com dívida conhecida (motivo aparente) descartado por escala/portaria que prova ausência no turno do desvio.
- **PAT-03 — Pista-código offline**: código de lote impresso no ticket de balança, cuja chave de leitura está no manual de codificação de silos (documento separado).

Mínimo exigido pela issue: 2. Este experimento mira usar PAT-01 e PAT-04 como núcleo, com PAT-02/03 como reforço se a estrutura comportar sem inflar o elenco além do limite recomendado para Intermediário (`docs/DIFFICULTY_FRAMEWORK.md`, ≤ 6 suspeitos).

---

## 2. Rubrica de playtest (RUB-01/02)

A QA automática (validator, estimador, clue_graph, obviousness_checker) não mede as dimensões abaixo.
Só o playtest humano mede. Esta rubrica é preenchida à mesa, após a sessão (STEP-05), pelos jogadores
e/ou pelo facilitador com base na reação observada.

### RUB-01 — Dimensões qualitativas (1 a 5 cada)

Escala: 1 = falha grave · 3 = aceitável com ressalva · 5 = nível de referência (calibração)

| # | Dimensão | Pergunta ao avaliar | Nota (1–5) | Nota do caso de calibração (referência, se disponível) | Observações |
|---|---|---|---|---|---|
| 1 | Pista não óbvia mas justa | A chave não foi adivinhada de cara, mas foi dedutível só com os documentos entregues? | _(preencher STEP-05)_ | — | |
| 2 | Textura humana dos documentos | Os textos soam escritos por pessoas reais (viés, omissão, tom), não por gabarito? | _(preencher STEP-05)_ | — | |
| 3 | Desorientação justa | Os red herrings enganaram sem trapacear — foram descartáveis pelos próprios documentos? | _(preencher STEP-05)_ | — | |
| 4 | Resolução merecida | A virada/solução recompensou o raciocínio do grupo, não "caiu de graça"? | _(preencher STEP-05)_ | — | |

Nota de uso: a coluna "nota do caso de calibração" só é preenchível se houver playtest comparável do
"Uma Noite Sem Flores" com a mesma rubrica; caso não exista, registrar `sem dado comparável` no STEP-05
em vez de forçar comparação.

### RUB-02 — Objetivo / mesa

| Métrica | Resultado |
|---|---|
| Grupo chegou ao suspeito correto no E1? | _(preencher STEP-05)_ |
| Grupo chegou ao culpado + destino da carga no E2? | _(preencher STEP-05)_ |
| Nº de dicas usadas (leve/média/forte) | _(preencher STEP-05)_ |
| Ponto de travamento observado (se houver) | _(preencher STEP-05)_ |
| Tempo real de mesa | _(preencher STEP-05)_ |
| Tempo declarado no blueprint | _(preencher STEP-02)_ |

---

## 3. Métricas de pipeline (STEP-03 + FIX-1, estado final aprovado)

| Ferramenta | Comando | Resultado | Observações |
|---|---|---|---|
| `validator --strict` | `python -m generator.validator examples/caso_gerado_cooperativa.json --strict` | Risco: médio-baixo. Pode gerar: SIM. Críticos: 0. Moderados: 1 (`DC_000` — sem dicas contextuais definidas). Avisos: 11 (`ELENCO_001` ×1, `GP_003` ×9, `CONT_002` ×1). | 0 críticos atende o critério strict; 1 moderado isolado é tolerado (regra de risco só falha com moderados ≥ 2). |
| Estimador de dificuldade | `estimate_difficulty`/`estimate_minutes` (`generator/playtest_metrics.py`) | `intermediario`, 85 min estimados (declarado no blueprint: `tempo_estimado_min: 100`). | Match de nível com o declarado. Delta estimado×declarado: −15 min (−15%). |
| `clue_graph` | `analyze_clue_graph` (`generator/clue_graph.py`) | `status: passed`. `summary`: 17 documentos, 5 contratos, 22 nodes, 12 edges, 1 solution_target. `solution_paths`: `C-FINAL` depth=4 (`E1-09`, `E2-04`, `E2-05` / contratos `C-E1-01`, `C-E2-01`, `C-E2-02`, `C-FINAL`). `issues`: só `GP_003` ×9 (warning), 0 `GP_007`. | depth=4 ≥ 2 atendido; sem `GP_007`. |
| `obviousness_checker` | `check_obviousness` | `ObviousnessReport(findings=[])`. | Zero findings — sem `OBV_001` (confissão) nem `OBV_009` (nome-em-ação). |
| PAT declarados e rastreáveis | inspeção do blueprint (STEP-02, preservado em STEP-03/FIX-1) | 4 de 4: **PAT-01** (log `E1-04` × regra de exclusividade `E1-02`, reforço `E1-03`, `pilares_validacao[0]`/`C-E1-01`), **PAT-02** (Tiago Bessa, motivo aparente em `E1-03`, descartado por `E2-07`, reforçado em `DICA-07`), **PAT-03** (código de lote `LT-04-02-C` em `E2-02`, chave em `E2-03`, `codigos[0]`), **PAT-04** (virada E1 "quem tinha acesso" → E2 "para onde foi a carga", `objetivos_por_envelope`, `E2-02`/`E2-04`/`E2-05`). | Excede o mínimo de 2 exigido por GEN-03. Rastreabilidade de PAT-01 foi objeto de rejeição e correção em STEP-03 FIX-1 (ver histórico da issue) — restaurada e reaprovada. |

---

## 4. Comparação com o caso de calibração (REP-01, faixa a — métricas de pipeline)

Fonte do lado calibração: `docs/CALIBRACAO_REFERENCIA_EXTERNA.md` (ISSUE-30.8 STEP-04). O JSON do caso de
calibração (`examples/caso_referencia_uma_noite_sem_flores.json`) não foi lido nesta comparação — só o
relatório já produzido.

| Dimensão | Gerado (cooperativa) | Calibração (Uma Noite Sem Flores) | Leitura |
|---|---|---|---|
| `validator --strict` | 0 críticos, 1 moderado (`DC_000`), 11 avisos | 0 críticos, 0 moderados, 14 avisos | Calibração está mais limpa (0 moderados vs 1). O moderado do gerado é ausência de dicas contextuais, correção pontual e não-narrativa — não indica problema estrutural equivalente aos avisos de conteúdo. |
| Estimador de dificuldade | `intermediario` (match com declarado), 85 min estimados vs 100 declarados (−15%) | `intermediario` (match com declarado), 90 min estimados vs 100 declarados (−10%) | Ambos batem o nível declarado. Ambos os estimadores de tempo subestimam frente ao declarado, gerado um pouco mais (−15% vs −10%) — consistente com a observação já registrada em `CALIBRACAO_REFERENCIA_EXTERNA.md` de que o estimador de tempo tende a subestimar casos com documentos de contexto extensos (ISSUE-31+, não corrigido aqui). |
| `clue_graph` — profundidade | `C-FINAL` depth=4 | depth=3 | Gerado tem 1 nível a mais de profundidade dedutiva formal na cadeia até o contrato final. Não permite concluir "mais difícil" sozinho — depth é só um dos sinais do estimador pós-30.7, e ambos convergem para `intermediario`. |
| `clue_graph` — documentos/nodes/edges | 17 docs, 22 nodes, 12 edges | 19 docs, 23 nodes, 11 edges | Volume similar, gerado ligeiramente mais enxuto (2 docs a menos). Nenhum dos dois usa volume como driver de dificuldade (pós-30.7). |
| `clue_graph` — órfãos/avisos estruturais | 9 `GP_003`, 0 `GP_004`, 0 `GP_007` | 11 `GP_003`, 1 `GP_004`, 0 `GP_007` | Ambos têm `GP_003` classificado como artefato de codificação (documentos de contexto/atmosfera não formam contrato por design). Gerado não usa o padrão "contrato de descarte" (`C-E1-DESCARTE`) que gerou o `GP_004` da calibração — descarte de Tiago Bessa (PAT-02) no gerado é feito via `red_herrings`/dica, não via contrato dedicado. Nenhum `GP_007` em nenhum dos dois — sem caminho quebrado até o contrato final. |
| `obviousness_checker` | zero findings | zero findings | Empate — ambos limpos de `OBV_001`/`OBV_009`. |
| Uso de padrões PAT | 4 de 4 (PAT-01..04), rastreáveis a IDs de documento/campo | fonte dos próprios PAT-01..04 (destilados deste corpus em ISSUE-30.10) | Não é comparação simétrica: a calibração é a origem dos padrões, o gerado é a primeira aplicação deliberada e rastreável deles num domínio novo. Uso confirmado, não inventado (STEP-02_REVIEW.md + STEP-03_FIX-1_REVIEW.md). |
| Elenco/papéis | executor=planejador=beneficiário no mesmo personagem (`ELENCO_001`), 7 personagens, 3 red herrings | executor + planejador/beneficiário concentrados em 2 personagens (`ELENCO_001`), 6 suspeitos, 3 red herrings | Ambos concentram papéis por design editorial (aviso não-bloqueante nos dois). Estrutura de elenco comparável em escala. |

### Leitura inicial (só faixa a — pipeline)

Nas métricas objetivas, o caso gerado do zero **iguala ou supera** o caso de calibração: 0 críticos em
ambos, profundidade formal maior (4 vs 3), obviousness limpo nos dois, uso de PAT confirmado e rastreável.
A única métrica em que a calibração é estritamente melhor é `validator --strict` (0 moderados vs 1,
`DC_000` — falta de dicas contextuais, correção mecânica sem custo narrativo).

**Isso não responde à pergunta do experimento.** Pipeline-verde é necessário, não suficiente (contrato
HUMAN-01 da issue). As métricas de pipeline não leem pista-não-óbvia-mas-justa, textura humana,
desorientação justa nem resolução merecida — exatamente as quatro dimensões da rubrica RUB-01, que é
muda aqui e só ganha dado real no playtest (STEP-05). A comparação completa (faixa b, rubrica humana) e
o veredito honesto (REP-02) ficam pendentes até a mesa.

---

## 5. Veredito honesto (REP-02, a preencher no STEP-05)

_(pendente — geramos no nível da referência? Onde os gaps aparecem — pista, textura, desorientação, resolução?
Cada gap vira recomendação, incluindo se aponta para a necessidade de um revisor qualitativo — gap 1 do
balanço de calibração 2026-06-29.)_

---

## Histórico

- STEP-01 (2026-07-02): domínio, parâmetros e rubrica RUB-01/02 definidos (esqueleto). Domínio escolhido:
  cooperativa agrícola / desvio de carga de grãos. PAT núcleo: PAT-01 + PAT-04, com PAT-02/PAT-03 como
  reforço candidato para o STEP-02.
- STEP-04 (2026-07-02): faixa (a) — métricas de pipeline (seção 3) preenchida com os resultados finais
  aprovados de STEP-03/FIX-1 (validator strict 0 críticos/1 moderado DC_000, estimador intermediario/85min,
  clue_graph C-FINAL depth=4 sem GP_007, obviousness zero findings, 4/4 PAT rastreáveis). Comparação inicial
  contra `docs/CALIBRACAO_REFERENCIA_EXTERNA.md` registrada (seção 4): gerado iguala ou supera a calibração
  nas métricas objetivas, mas isso não responde ao experimento — falta a faixa (b), rubrica humana (RUB-01/02),
  que segue como placeholder até o playtest. Rubrica RUB-01/02 (seção 2) conferida íntegra, não reescrita.
  Issue pausada: `NEXT_ACTION: human`, aguardando playtest humano (STEP-05).
