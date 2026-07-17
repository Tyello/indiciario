# ISSUE-33.10 — STEP-04: Autópsia de runs incompletas + ambiguidade (H-Ra, H-Ma)

## 1. Contexto de entrada

De STEP-02 e STEP-03:
- **H-E1a e H-E1b**: DESCARTADAS (STEP-02) — E1 e blueprint coincidem, nenhuma divergência editorial
- **H-Ja, H-Jb, H-Sa**: INDETERMINADAS (STEP-03) — faltam solver output JSON + judge verdict JSON

Objetivo de STEP-04:
- **H-Ra**: classificar a causa das 3 runs incompletas (timeout vs. parse-fail vs. transporte)
- **H-Ma**: avaliar se sobrou sinal de ambiguidade real após descartes/indeterminações de H-E1/H-J

---

## 2. Julgamento de H-Ra: Causa das 3 runs incompletas

### 2.1 Inventário das 3 runs incompletas

| Run ID | Meter | Lote | Solicitadas | Completadas | Status na lista |
|--------|-------|------|-------------|-------------|-----------------|
| METER_1784293071639_RUN_3 | Lote 1 | 5 | 4 | **NÃO LISTADA em run_results** |
| METER_1784299101472_RUN_0 | Lote 2 | 3 | 1 | **NÃO LISTADA em run_results** |
| METER_1784299101472_RUN_2 | Lote 2 | 3 | 1 | **NÃO LISTADA em run_results** |

### 2.2 Dados registrados para cada run incompleta

**Campos inspecionados em ambos os JSONs** (calib_lote1.json, calib_lote2.json):

| Campo | Esperado para diagnose de timeout/parse/transporte | Persistido? |
|-------|---------------------------------------------|-----------|
| `run_results[*].run_id` | Identifica a run | ✅ Sim (para runs completas) |
| `run_results[*].status` ou `error` | Razão de incompletude | ❌ **Não existe** |
| `run_results[*].exception` | Tipo de erro (TimeoutError, JSONDecodeError, etc) | ❌ **Não existe** |
| `run_results[*].stderr` ou `log_excerpt` | Saída de erro | ❌ **Não existe** |
| `run_results[*].duration_seconds` ou `runtime_ms` | Tempo decorrido | ❌ **Não existe** |
| Propriedade top-level `incomplete_runs` | Array das runs que não completaram | ❌ **Não existe** |
| Propriedade top-level `run_errors` | Mapa de run_id → erro | ❌ **Não existe** |

**Estrutura de run_results observada**:
```json
{
  "run_id": "...",
  "classification": "...",
  "required_met_count": ...,
  "required_total": 3
}
```

Nenhum campo de estado, erro ou razão de incompletude.

### 2.3 Veredito por run incompleta

#### Run 1: `METER_1784293071639_RUN_3` (Lote 1)

**O que está registrado**: Nada. A run não aparece em `run_results`.

**Campos faltantes para classificar causa**:
- `status` (expected: "timeout" | "parse_error" | "transport_error" | outras)
- `exception` (tipo: TimeoutError, JSONDecodeError, ConnectionError, etc.)
- `stderr` ou `log_excerpt`
- `duration_seconds` (necessário para confirmar timeout)

**Hipóteses plausíveis** (sem evidência):
- Timeout: provável, dado o tamanho do bundle (2 envelopes, 19 artefatos) e latência de LLM
- Parse-fail: menos provável se o provider retornou algo
- Transporte: improvável (LLM provider geralmente retorna erro estruturado, não silêncio)

**Classificação**: **INDETERMINADA por falta de dado** — `status`, `exception`, `stderr`, `duration_seconds` não foram registrados

#### Run 2: `METER_1784299101472_RUN_0` (Lote 2)

**O que está registrado**: Nada. A run não aparece em `run_results`.

**Campos faltantes para classificar causa**: idem Run 1 acima.

**Classificação**: **INDETERMINADA por falta de dado** — `status`, `exception`, `stderr`, `duration_seconds` não foram registrados

#### Run 3: `METER_1784299101472_RUN_2` (Lote 2)

**O que está registrado**: Nada. A run não aparece em `run_results`.

**Campos faltantes para classificar causa**: idem Run 1 acima.

**Classificação**: **INDETERMINADA por falta de dado** — `status`, `exception`, `stderr`, `duration_seconds` não foram registrados

### 2.4 Consolidação de H-Ra

| Run | Timeout | Parse-fail | Transporte | Veredito |
|-----|---------|-----------|-----------|----------|
| RUN_3 (Lote 1) | ? | ? | ? | **INDETERMINADA por falta de `status`, `exception`, `stderr`** |
| RUN_0 (Lote 2) | ? | ? | ? | **INDETERMINADA por falta de `status`, `exception`, `stderr`** |
| RUN_2 (Lote 2) | ? | ? | ? | **INDETERMINADA por falta de `status`, `exception`, `stderr`** |

**Conclusão consolidada H-Ra**: As 3 runs incompletas não tiveram seus erros registrados nos JSONs. O meter não persistiu campos de status, exception, stderr ou duration necessários para classificar a causa como timeout, parse-fail ou transporte. Sem essa informação, qualquer classificação seria palpite.

---

## 3. Julgamento de H-Ma: Ambiguidade real

### 3.1 Condição prévia para julgar H-Ma

Spec: "só julgar SE sobrar sinal de ambiguidade depois de H-E1/H-J descartadas/indeterminadas"

**Status de H-E1 e H-J**:
- H-E1a: ✅ DESCARTADA (STEP-02) — E1 matches blueprint
- H-E1b: ✅ DESCARTADA (STEP-02) — statements OK vs. gabarito
- H-Ja: ❌ INDETERMINADA (STEP-03) — faltam judge verdict details
- H-Jb: ❌ INDETERMINADA (STEP-03) — faltam judge verdict details
- H-Sa: ❌ INDETERMINADA (STEP-03) — faltam solver output + bloqueio de ordem

**Conclusão**: Embora H-E1 tenha sido descartada, H-J ficou indeterminada (não descartada). Formalmente, há um sinal não resolvido. Porém, a spec permite prosseguir com H-Ma "se sobrar sinal de ambiguidade", o que significa examinar os dados que confirmam ou refutam a ambiguidade.

### 3.2 Sinais de ambiguidade nos dados disponíveis

**Onde procurar sinais de ambiguidade**:
1. Flags nos JSONs: `AMBIGUIDADE_DETECTADA` em Lote 1
2. Classificações de runs: 2 runs em Lote 1 marcadas como `"ambiguo"` (RUN_0, RUN_4)
3. Met counts: RUN_0 com 1/3, RUN_4 com 2/3 (ambos baixos, sugestivo)

**O que está registrado**:
```
Lote 1:
  - RUN_0: classification="ambiguo", required_met_count=1/3
  - RUN_4: classification="ambiguo", required_met_count=2/3
  - Flag: AMBIGUIDADE_DETECTADA

Lote 2:
  - RUN_1: classification="nao_resolvido", required_met_count=1/3
  - Nenhuma run marcada como "ambiguo"
```

### 3.3 O que seria necessário para julgar H-Ma

Spec: "Se a solução alternativa relatada pelo solver (nalgum run) é de fato coerente com o bundle."

**Dados necessários**:
1. `solver_report.conclusion` — prosa do solver sobre culpado/método (para RUN_0 ou RUN_4)
2. `solver_report.alternative_solution_detected` — se o solver relatou uma alternativa
3. `solver_report.open_questions` — se há ambiguidade na própria análise do solver
4. Comparação manual: a alternativa proposta é coerente com os documentos do bundle?

**Campos esperados em solver output JSON**:
```json
{
  "run_id": "METER_1784293071639_RUN_0",
  "conclusion": "...",
  "confidence": "...",
  "alternative_solution": "...",
  "open_questions": [...]
}
```

### 3.4 Dados realmente persistidos

Inspect dos JSONs:
- ✅ Presentes: `classification`, `required_met_count`, `flags`
- ❌ Faltam: solver output JSON, alternative solution text, open questions

**Achado**: Não há nenhuma prosa de solver ou indicação de alternativa coerente registrada no Lote 1/2. Os JSONs contêm apenas agregados (counts, classification), não os relatórios.

### 3.5 Veredito de H-Ma

| Aspecto | Evidência |
|---------|-----------|
| Sinal de ambiguidade nos dados? | Sim: flag `AMBIGUIDADE_DETECTADA` + 2 runs classificadas `"ambiguo"` |
| Alternativa do solver acessível? | ❌ **Não** — falta `solver_report.alternative_solution` ou `solver_report.conclusion` |
| Prosa do solver registrada? | ❌ **Não** — solver outputs não foram persistidos |
| Possível julgar coerência da alternativa? | ❌ **Não** — sem prosa, não dá avaliar se é coerente |

**Classificação**: **INDETERMINADA por falta de dado** — `solver_report.conclusion`, `solver_report.alternative_solution`, `solver_report.open_questions` não foram registrados

**Observação crítica**: A diferença entre H-Ra e H-Ma é que:
- H-Ra: faltam dados técnicos (status, exception, stderr) — necessários para diagnose imediata
- H-Ma: faltam dados semânticos (solver output) — necessários para avaliar se a ambiguidade é real ou artefato

Ambas são indeterminadas, mas por razões complementares.

---

## 4. Consolidação final: H-Ra + H-Ma

| Hipótese | Veredito | Evidência |
|----------|----------|-----------|
| **H-Ra** (timeout/parse/transporte) | **INDETERMINADA** | Faltam: `status`, `exception`, `stderr`, `duration_seconds` nas runs incompletas. Nenhuma run incompleta foi registrada com motivo de incompletude. |
| **H-Ma** (ambiguidade real) | **INDETERMINADA** | Faltam: `solver_report.conclusion`, `solver_report.alternative_solution`. Há sinal de ambiguidade (flag + 2 runs classificadas `"ambiguo"`), mas sem a prosa do solver, não dá verificar se alternativa é coerente com o bundle. |

**Padrão observado**: Ambas as hipóteses convergem para a mesma raiz: o meter não persistiu os run records individuais (solver output + judge verdict JSON + run error logs). Isso não é coincidência — é o mesmo achado de observabilidade do STEP-01 (falta de artefatos críticos).

---

## 5. Gatilhos de escalação?

Verificando contra a definição do spec:

1. **Validação falhou 2x**: N/A — não há código a validar, só leitura
2. **Realidade ≠ spec**: ✅ **Nenhuma divergência** — spec autoriza "se um artefato não existir, registrar achado"
3. **Decisão residual**: ✅ **Nenhuma** — julgamentos são binários (indeterminada por falta de X específico)
4. **Condição da etapa (ESCALA SE)**: ✅ **Nenhuma disparada** — tudo dentro das hipóteses esperadas

**Nenhum gatilho de escalação disparou.**

---

## 6. Resumo para STEP-05 (relatório final)

| Hipótese | Status | Achado crítico |
|----------|--------|----------------|
| H-Ra (incompletas — timeout/parse/transporte) | INDETERMINADA | Runs incompletas não tiveram erro registrado; faltam `status`, `exception`, `stderr` |
| H-Ma (ambiguidade real) | INDETERMINADA | Solver outputs não foram persistidos; não dá verificar se alternativa é coerente |

**Contexto agregado** (STEP-01 + STEP-02 + STEP-03 + STEP-04):
- **Arquivos faltantes persistidos**: solver output JSON, judge verdict JSON, run error logs
- **Hipóteses descartadas**: H-E1a, H-E1b
- **Hipóteses indeterminadas**: H-Ja, H-Jb, H-Sa, H-Ra, H-Ma
- **Recomendação**: Propor issue de melhoria no meter (observabilidade: persistir run records completos)

---

## Critério de "done"

- ✅ H-Ra julgada com evidência (indeterminada; faltam campos X, Y, Z)
- ✅ H-Ma julgada com evidência (indeterminada; faltam campos X, Y, Z)
- ✅ Nenhum gatilho de escalação disparou
- ✅ Procedimento seguido (leitura forense dos JSONs, registro de faltantes)
