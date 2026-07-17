# ISSUE-33.10 — STEP-01: Inventário de artefatos da calibração 33.9

## 1. Artefatos encontrados

### Estrutura de diretórios
```
calibration/
  ├── bundle_hashes.json
  ├── expected_uma_noite_sem_flores.json
  ├── bundles/
  │   └── BUNDLE-CALIB-UMANOITESEMFLORES-01/
  │       ├── blind_bundle_manifest.yaml
  │       └── player/
  │           ├── E1-00.md a E1-09.md (10 arquivos)
  │           └── E2-00.md a E2-08.md (9 arquivos)
  └── reports/
      ├── calib_lote1.json
      └── calib_lote2.json
```

### Detalhamento por artefato

| Caminho | Tipo | Tamanho | Conteúdo em alto nível | Created | Modificado |
|---------|------|--------|----------------------|---------|-----------|
| `calibration/bundle_hashes.json` | report | 363 B | Hash SHA256 do bundle, contagem de artifacts incluídos (19), flag leak_check_valid=true | 2026-07-12 | 2026-07-12 |
| `calibration/expected_uma_noite_sem_flores.json` | E1 | 1.3 KB | 4 conclusões esperadas (culpado, método, motivo, descarte_rui), lista de 6 key_evidence_ids: ART-E1-02, ART-E1-03, ART-E2-04, ART-E2-03, ART-E2-07, ART-E2-08 | 2026-07-12 | 2026-07-12 |
| `calibration/bundles/BUNDLE-CALIB-UMANOITESEMFLORES-01/blind_bundle_manifest.yaml` | manifest | 19.4 KB | Manifest v1.0 com 19 artifacts listados (ART-E1-00 a ART-E1-09, ART-E2-00 a ART-E2-08), visibilidade public_player, sem gabarito (contains_solution=false) | 2026-07-12 | 2026-07-12 |
| `calibration/bundles/BUNDLE-CALIB-UMANOITESEMFLORES-01/player/E1-{00..09}.md` | player_document (10 files) | 950–2789 B cada | Documentos do enunciado E1 do caso "Uma Noite Sem Flores" — entrevistas, evidências físicas, cronologia | 2026-07-12 | 2026-07-12 |
| `calibration/bundles/BUNDLE-CALIB-UMANOITESEMFLORES-01/player/E2-{00..08}.md` | player_document (9 files) | 816–1796 B cada | Documentos do enunciado E2 (segunda onda de investigação) | 2026-07-12 | 2026-07-12 |
| `calibration/reports/calib_lote1.json` | solvability_report | 1.5 KB | METER_1784293071639: 5 runs solicitadas, **4 completadas** (RUN_3 incompleta); classificações: ambiguo (RUN_0, RUN_4), vazamento (RUN_1), nao_resolvido (RUN_2); solve_rate=0.0; flags=[AMBIGUIDADE_DETECTADA, VAZAMENTO_DETECTADO, RUNS_INCOMPLETAS] | 2026-07-17 10:06 | 2026-07-17 10:06 |
| `calibration/reports/calib_lote2.json` | solvability_report | 1.0 KB | METER_1784299101472: 3 runs solicitadas, **1 completada** (RUN_0 e RUN_2 incompletas); classificação: nao_resolvido (RUN_1); solve_rate=0.0; flags=[RUNS_INCOMPLETAS] | 2026-07-17 11:50 | 2026-07-17 11:50 |

### Summary de métricas agregadas por report

#### Lote 1 (METER_1784293071639)
- **Runs solicitadas**: 5
- **Runs completadas**: 4
- **Runs incompletas**: 1 (RUN_3)
- **Classificações**:
  - `resolvido`: 0
  - `nao_resolvido`: 1 (RUN_2)
  - `vazamento`: 1 (RUN_1)
  - `ambiguo`: 2 (RUN_0, RUN_4)
- **Solve rate**: 0.0
- **Difficulty estimate**: `injusto`
- **Flags**: `AMBIGUIDADE_DETECTADA`, `VAZAMENTO_DETECTADO`, `RUNS_INCOMPLETAS`
- **Provider**: `claude-code`
- **Temperature**: null (provider-controlled)
- **Prompts**: SHA256 hashes armazenados (solver e judge v1)

#### Lote 2 (METER_1784299101472)
- **Runs solicitadas**: 3
- **Runs completadas**: 1
- **Runs incompletas**: 2 (RUN_0, RUN_2)
- **Classificações**:
  - `resolvido`: 0
  - `nao_resolvido`: 1 (RUN_1)
  - `vazamento`: 0
  - `ambiguo`: 0
- **Solve rate**: 0.0
- **Difficulty estimate**: `injusto`
- **Flags**: `RUNS_INCOMPLETAS`
- **Provider**: `claude-code`
- **Temperature**: null (provider-controlled)
- **Prompts**: SHA256 hashes armazenados (solver e judge v1)

---

## 2. Artefatos FALTANTES (achados de observabilidade)

| Artefato faltante | Necessário para | Impacto |
|-------------------|-----------------|--------|
| **Run records de solver (JSON)** — um por run completada | H-Sa (validar se solver realmente resolveu ou só pegou a prosa errada) | Alto — sem visualizar a solução proposição do solver, não é possível classificar se o erro está na prosa (H-Sa) vs. no judge (H-Ja/Jb). Cegamente assumindo lote1/lote2 foram ambos "nao_resolvido", mas o RUN_1 está marcado "vazamento" — essa contradição exigiria ler o output do solver. |
| **Judge verdicts (JSON)** — um por run completada | H-Ja/H-Jb (validar se judge descartou corretas, ou se solver errou mesmo) | Alto — mesmo problema: sem o veredito do judge item-a-item (met/not_met, rationale, evidence_cited), não dá distinguir culpa: solver errou, ou judge rebaixou sem motivo? |
| **Stderr/logs das runs incompletas** | H-Ra (classificar: timeout vs. parse-fail vs. transporte) | Médio — Lote 1 RUN_3 incompleta, Lote 2 RUN_0/RUN_2 incompletas. Sem logs, não dá saber se travou, parse falhou, ou erro de transport. Assumindo timeout por tamanho do dossiê, mas é palpite. |
| **Timestamps de início/fim por run** | Correlação de timeout vs. tamanho | Baixo — ajudaria a confirmar H-Ra (se RUN_3 rodou 30min → timeout provável; se rodou 1s → parse-fail provável) |
| **Metadata de execução (modelo específico, versão, hash dos datos de entrada)** | Reproduzibilidade | Médio — "claude-code" como provider, mas qual modelo? (sonnet na ISSUE-33.9 STEP-06, mas spec é agnóstica). Sem entrada exata dos dados de entrada, não dá reproduzir. |
| **Cópia isolada do E1 usado no bundle** (congelado em momento de execução) | Validar H-E1a/H-E1b | Baixo — `expected_uma_noite_sem_flores.json` é o esperado, mas é também o **esperado no diagnóstico**. Se o E1 foi modificado entre STEP-01 (geração) e STEP-04 (calibração), isso passa invisível. Não crítico agora, mas bom registrar. |
| **Hash ou snapshot do bundle no momento de execução** | Reproduzibilidade bit-for-bit | Baixo — `bundle_hashes.json` tem o SHA do bundle, então dá validar. Não é falta crítica. |

**Conclusão**: As 2 primeiras faltas (solver outputs + judge verdicts) são **críticas** — sem elas, as hipóteses H-Sa e H-Ja/Jb não podem ser julgadas. Isso é um defeito sério de observabilidade no meter.

---

## 3. IDs de runs para autópsia detalhada (STEP-03 e STEP-04)

### Run de VAZAMENTO (para STEP-03)
- **ID**: `METER_1784293071639_RUN_1` (Lote 1)
- **Classificação**: `vazamento`
- **Required met**: 2/3
- **Por que foi selecionada**: É a única run vazamento nos dados. A lógica: solver resolveu (atingiu conclusão correta) mas o judge descartou porque a evidência não foi citada formalmente. Sem o solver output + judge verdict, assume-se essa hipótese; com eles, poderia ser outra coisa.

### Run INCOMPLETA (para STEP-04)
- **ID**: `METER_1784293071639_RUN_3` (Lote 1) — primeira escolha
  - **Por que**: Run 3 de 5. Sem logs, não dá saber causa.
- **ID alternativa**: `METER_1784299101472_RUN_0` (Lote 2)
  - **Por que**: Lote 2 é mais grave (1/3 completas vs. 4/5). Mas ambas servem para H-Ra.

---

## 4. Gatilhos de escalação?

Nenhum gatilho de escalação detectado neste STEP:
- ✅ E1 (expected_uma_noite_sem_flores.json) existe
- ✅ Bundle manifest existe e lista artifacts
- ✅ E1 documents (player/) existem em número consistente com manifest
- ✅ Reports (calib_lote1, calib_lote2) existem e são válidos per schema
- ✅ key_evidence_ids no E1 (6 ids) é verossímil — serão validados em H-E1a
- ✅ Nenhuma decisão residual — inventário puro, sem julgar hipóteses

**Observação**: A falta de run records individuais é um achado, não um bloqueador — a spec autoriza "se algum artefato não tiver sido persistido, isso é um achado".

---

## 5. Resumo para STEP-02..05

| Step | Foco | Precisa de | Status pré-requisito |
|------|------|-----------|---------------------|
| STEP-02 | H-E1a, H-E1b (E1 e bundle) | E1 esperado ✅, manifest ✅, bundle ✅ | ✅ Pronto |
| STEP-03 | H-Ja, H-Jb, H-Sa (solver+judge) | METER_1784293071639_RUN_1 output + verdict | ❌ **Faltam artefatos** — solver output JSON não existe, judge verdict JSON não existe |
| STEP-04 | H-Ra, H-Ma (incompletas + ambig) | Logs de RUN_3, metadata | ❌ **Faltam artefatos** — stderr/logs não foram persistidos |
| STEP-05 | Compilar diagnóstico | STEP-02..04 | Depende de STEP-03/04 |

---

## Arquivo de saída

Este relatório foi gerado em `.ai/runs/ISSUE-33.10/STEP-01_EXECUTION.md`.

Próximo: STEP-02 (julgar H-E1a/H-E1b com dados disponíveis).
