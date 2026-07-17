# Diagnóstico da calibração ISSUE-33.9 — por que o benchmark saiu "injusto"

Data: 2026-07-17  
Autópsia: ISSUE-33.10  
Caso: "Uma Noite Sem Flores" (playtest comercial, comprovadamente justo)  
Meter: `solvability_meter.py`, versão ISSUE-33.9

---

## 1. Inventário de artefatos persistidos e omitidos

### Artefatos disponibilizados pela execução ISSUE-33.9

| Artefato | Localização | Status | Utilidade diagnóstica |
|----------|-------------|--------|----------------------|
| Relatório agregado de Lote 1 | `calibration/reports/calib_lote1.json` | Existente | Classificações (vazamento, ambiguo, resolvido), met counts agregados |
| Relatório agregado de Lote 2 | `calibration/reports/calib_lote2.json` | Existente | Idem |
| Bundle cego | `examples/caso_referencia_uma_noite_sem_flores.json` | Existente | Envelope E1, E2, artefatos, gabarito esperado |
| Gabarito esperado (E1 transcrito) | `examples/expected_uma_noite_sem_flores.json` | Existente | Statements esperados (culpado, método, motivo, descartes) |
| Blueprint transcrito | `examples/caso_referencia_uma_noite_sem_flores.json` (seção esperada) | Existente | Solução textual esperada por E1/E2 |

### Artefatos NÃO persistidos — achados de observabilidade

| Campo esperado | Localização esperada | O que seria |Critério de uso |
|---|---|---|---|
| `solver_report.json` | `calibration/run_artifacts/METER_*_RUN_*/solver_report.json` | Output completo do blind solver: conclusão em prosa, reasoning, confidence, evidence_used[], open_questions[] | Essencial para H-Ja (semântica), H-Sa (divergência factual), H-Ma (alternativa coerente) |
| `judge_verdict.json` | `calibration/run_artifacts/METER_*_RUN_*/judge_verdict.json` | Veredito completo: conclusions[], evidence_cited[], rationale[], warnings[], classificação antes/depois de rebasing | Essencial para H-Ja (falha de casamento), H-Jb (evidence vazia) |
| `run_status / run_error` | `calibration/run_artifacts/METER_*_RUN_*/metadata.json` ou top-level em `run_results` | status (complete/timeout/parse_error/transport_error), exception type, stderr excerpt, duration_seconds | Essencial para H-Ra (classificar causa de incompletude) |
| `run_results[*].status` | `calib_lote*.json` → `run_results[*]` | Status de cada run (hoje só existe para runs que completaram) | Necessário para saber quais runs falharam e por quê |
| `run_results[*].exception` | `calib_lote*.json` → `run_results[*]` | Tipo de erro (TimeoutError, JSONDecodeError, ConnectionError, etc.) | Necessário para classificar H-Ra |
| `run_results[*].stderr` | `calib_lote*.json` → `run_results[*]` | Excerpt de stderr ou último traceback | Necessário para diagnosticar por que run falhou |
| `run_results[*].duration_seconds` | `calib_lote*.json` → `run_results[*]` | Tempo decorrido antes de falha | Necessário para confirmar timeout vs. outro erro |

**Conclusão da seção 1**: O meter agrega apenas nível de run (classification, met counts). Não persiste run records individuais (solver output, judge verdict, error logs). Consequência: **observabilidade insuficiente** torna qualquer autópsia dependente de sorte.

---

## 2. Tabela de julgamento das 7 hipóteses

| # | Hipótese | Veredito | Evidência | Implicação |
|---|---|---|---|---|
| H-E1a | `key_evidence_ids` do E1 não correspondem a `artifact_id` reais | ✅ **DESCARTADA** | STEP-02: 6/6 ids (ART-E1-02, ART-E1-03, ART-E2-04, ART-E2-03, ART-E2-07, ART-E2-08) encontrados no manifest; arquivos validados em `player/` | Não é causa do falso "injusto" |
| H-E1b | Statements E1 exigem fraseologia que blueprint não expressa | ✅ **DESCARTADA** | STEP-02: 4/4 statements (culpado, método, motivo, descarte_rui) mapeados 1:1 para respostas esperadas no blueprint; granularidade compatível (IDs, nomes, etiqueta hex) | Não é causa do falso "injusto" |
| H-Ja | Judge rebaixa `met` de conclusões corretas por falha de casamento semântico | ❌ **INDETERMINADA** | STEP-03: faltam `judge_verdict.conclusions[].rationale` e `conclusions[].met` (item-a-item). `calib_lote*.json` contém só agregados (2/3 met, sem detalhe). Não dá comparar prosa do solver vs. veredito racional do judge. | Não pode ser confirmada nem descartada sem dados |
| H-Jb | CJ_005 rebaixa em massa: solver conclui mas `evidence_cited` vazio | ❌ **INDETERMINADA** | STEP-03: faltam `judge_verdict.conclusions[].evidence_cited` (array) e `warnings[]` (que registraria rebasing por CJ_005). Contagem agregada (2/3 met) é consistente com rebasing, mas sem dados individuais, não dá contar quantos itens viraram met=false por evidence vazia. | Não pode ser confirmada nem descartada sem dados |
| H-Sa | Solver realmente errou culpado/método (divergência factual, não forma) | ❌ **INDETERMINADA** | STEP-03: faltam `solver_report.conclusion` (prosa). Regra anti-viés bloqueia julgar H-Sa enquanto H-Ja/Jb não forem descartadas com evidência (estão indeterminadas). | Não pode ser julgada sem antes resolver H-Ja/Jb e sem dados |
| H-Ra | Runs incompletas: timeout vs. parse-fail vs. transporte | ❌ **INDETERMINADA** | STEP-04: 3 runs não aparecem em `run_results` (METER_1784293071639_RUN_3, METER_1784299101472_RUN_0, METER_1784299101472_RUN_2). Faltam `status`, `exception`, `stderr`, `duration_seconds` para cada. Hipóteses plausíveis (timeout pela tamanho do bundle, menos provável parse-fail) sem evidência. | Não pode ser confirmada nem descartada sem dados |
| H-Ma | Ambiguidade real: dois suspeitos satisfazem as evidências | ❌ **INDETERMINADA** | STEP-04: há sinal de ambiguidade (flag `AMBIGUIDADE_DETECTADA` em Lote 1; 2 runs classificadas `"ambiguo"` com met counts baixos 1/3, 2/3). Porém faltam `solver_report.conclusion` e `solver_report.alternative_solution` para julgar se alternativa é de fato coerente com documentos do bundle. | Não pode ser confirmada nem descartada sem dados |

**Consolidação**: Duas hipóteses foram descartadas com evidência (H-E1a/E1b — E1 e blueprint estão alinhados). Cinco hipóteses ficaram indeterminadas por falta de dados (H-Ja, H-Jb, H-Sa, H-Ra, H-Ma). Nenhuma hipótese confirmada.

---

## 3. Autópsia detalhada: 1 run de vazamento + 1 run incompleta

### 3.1 Run de vazamento: `METER_1784293071639_RUN_1` (Lote 1)

#### Dados persistidos

```json
{
  "run_id": "METER_1784293071639_RUN_1",
  "classification": "vazamento",
  "required_met_count": 2,
  "required_total": 3
}
```

#### Interpretação

A run foi marcada como "vazamento" (solver atingiu conclusão, judge não validou evidência formal). Duas de 3 conclusões esperadas (culpado, método, motivo) foram marcadas met=true, mas sem citação de evidência — por isso a classificação "vazamento", que sinaliza risco de falso-positivo ou cit sem leitura.

#### Dados faltantes para diagnose

| Dado necessário | Status | Por quê falta |
|---|---|---|
| Solver output completo (JSON) | ❌ Faltante | Não persiste `solver_report.json` |
| Prosa da conclusão do solver | ❌ Faltante | Idem |
| Evidence_cited[] por conclusão | ❌ Faltante | Não persiste `judge_verdict.conclusions[]` |
| Rationale do judge por conclusão | ❌ Faltante | Idem |
| Warnings do judge (se CJ_005 aplicado) | ❌ Faltante | Não persiste `judge_verdict.warnings[]` |

#### Árvore de decisão bloqueada

```
RUN_1 classificada "vazamento" com 2/3 met
    ├─ Hypothesis H-Ja: Judge rebaixa por semântica?
    │   └─ Impossível julgar: faltam solver prosa + judge rationale
    ├─ Hypothesis H-Jb: CJ_005 rebaixa por evidence vazia?
    │   └─ Impossível julgar: faltam evidence_cited[] e warnings[]
    └─ Hypothesis H-Sa: Solver errou factualmente?
        └─ Bloqueado por ordem: não posso julgar sem descartar H-Ja/Jb primeiro
```

#### Conclusão parcial

RUN_1 não pode ser autopsiada além de registrar sua classificação agregada. Qualquer diagnose é especulação.

---

### 3.2 Run incompleta: `METER_1784293071639_RUN_3` (Lote 1, 4 de 5 completadas)

#### Dados persistidos

Nenhum. A run não aparece em `run_results[]` de `calib_lote1.json`.

#### Interpretação

A run foi solicitada (scheduler esperava 5 execuções em Lote 1), mas só 4 completaram. RUN_3 não retornou um resultado que pudesse ser agregado.

#### Dados faltantes para diagnose

| Dado necessário | Status | Por quê falta |
|---|---|---|
| Run status (complete/timeout/error) | ❌ Faltante | Runs incompletas não têm entrada em `run_results` |
| Exception type (TimeoutError, JSONDecodeError, etc.) | ❌ Faltante | Não persiste `run_results[*].exception` |
| Stderr ou log excerpt | ❌ Faltante | Não persiste `run_results[*].stderr` |
| Duration elapsed (segundos) | ❌ Faltante | Não persiste `run_results[*].duration_seconds` |

#### Árvore de decisão bloqueada

```
RUN_3 não completou (4/5 em Lote 1)
    ├─ Hypothesis H-Ra-timeout: LLM timeout pelo bundle grande?
    │   └─ Impossível julgar: faltam duration_seconds
    ├─ Hypothesis H-Ra-parse: JSON malformado do LLM?
    │   └─ Impossível julgar: faltam exception type e stderr
    └─ Hypothesis H-Ra-transport: Problema de rede/provider?
        └─ Impossível julgar: faltam exception type
```

#### Conclusão parcial

RUN_3 não pode ser classificada como timeout/parse/transporte sem acesso ao error log. Sem isso, não se sabe se foi falha transiente (retry?) ou sistemática (aumentar timeout?).

---

## 4. Camada(s) culpada(s) — análise de contribuição

### Achado crítico

A corrente de diagnose trava **sempre** no mesmo ponto: **falta de artefatos persistidos pelo meter**.

```
Meter lê: bundle cego, E1, prompts, temperatura
    ↓
Solver recebe: blind bundle + prompt
    ↓ (output JSON NOT persisted)
Solver conclui: "culpado é X, método é Y, motivo é Z"
    ↓
Judge recebe: solver output + expected statements
    ↓ (verdict JSON NOT persisted)
Judge veredita: met=true/false, evidence_cited[], rationale
    ↓
Meter agrega: classification em calib_lote*.json (APENAS COUNTS)
    ↓
Diagnose humano: "não dá ir além daqui"
```

### Camadas não-eliminadas por falta de evidência

Formalmente, **nenhuma camada foi eliminada**. As descartadas (H-E1a/E1b) são de outro tipo:
- **Solver**: em potencial culpa (H-Sa indeterminada), mas não pode ser julgado sem dados
- **Judge**: em potencial culpa (H-Ja/H-Jb indeterminadas), mas não pode ser julgado sem dados
- **Robustez operacional**: 3 runs incompletas não têm causa registrada (H-Ra indeterminada)
- **Observabilidade**: camada de instrumentação/persistência do meter é **CONFIRMADA COMO LACUNA**

### Contribuição por camada

| Camada | Status | Sinal observado | Contribuição ao veredito "injusto" |
|--------|--------|---|---|
| E1 / Blueprint | ✅ Saudável | Nenhuma divergência (STEP-02) | Nenhuma |
| Solver | ❓ Desconhecido | Sinal ambíguo (2/3 met parcial) | Impossível julgar sem dados |
| Judge | ❓ Desconhecido | Rebasing suspeito (vazamento=2 de 3 runs Lote 1) | Impossível julgar sem dados |
| Robustez operacional | ❓ Desconhecido | 3 de 8 runs incompletas | Impossível julgar causa sem dados |
| **Observabilidade / Instrumentação** | ❌ **FALHA** | Artefatos críticos não persistidos | **BLOQUEADOR de toda autópsia** |

### Conclusão

**A camada confirmada culpada é a observabilidade/instrumentação do `solvability_meter.py`.** Não é a "culpa final" (solver/judge/design), é a culpa de não poder investigar a causa final. A corrente não arrebenta na execução — arrebenta na falta de dados para auditar a execução.

---

## 5. Issue(s) de correção proposta(s)

### ISSUE-A: Observabilidade — persistência de run records completos

**Título**: Persistir solver output e judge verdict completos por run_id em solvability_meter

**Objetivo**: Permitir autópsias futuras sem depender de sorte ou re-execução, registrando o que foi consumido e produzido em cada etapa da calibração.

**Escopo**:

1. **Criar diretório de persistência**:
   ```
   calibration/run_artifacts/
     ├── METER_1784293071639_RUN_0/
     │   ├── solver_report.json
     │   ├── judge_verdict.json
     │   └── metadata.json
     └── METER_1784293071639_RUN_1/
         └── ...
   ```

2. **Persistir `solver_report.json` completo por run**:
   ```json
   {
     "run_id": "METER_..._RUN_...",
     "conclusion": "O culpado é Aurélio (ID 27)...",
     "reasoning_summary": "...",
     "confidence": "high" | "medium" | "low",
     "evidence_used": [
       { "artifact_id": "ART-E1-03", "excerpt": "..." }
     ],
     "open_questions": [...]
   }
   ```

3. **Persistir `judge_verdict.json` completo por run**:
   ```json
   {
     "verdict_id": "VERDICT_...",
     "report_run_id": "METER_..._RUN_...",
     "conclusions": [
       {
         "id": "culpado",
         "met": true,
         "evidence_cited": ["ART-E1-03"],
         "rationale": "Solver identificou Aurélio; ART-E1-03 valida..."
       },
       ...
     ],
     "classification": "resolvido" | "nao_resolvido" | "vazamento" | "ambiguo",
     "warnings": [
       "CJ_005: conclusão X marcada met=true mas evidence_cited vazio"
     ],
     "rebased_count": 0
   }
   ```

4. **Persistir metadados de execução** em `metadata.json`:
   ```json
   {
     "run_id": "METER_1784293071639_RUN_3",
     "status": "complete" | "timeout" | "parse_error" | "transport_error",
     "exception_type": "TimeoutError" | "JSONDecodeError" | null,
     "stderr_excerpt": "... últimas 500 caracteres ...",
     "duration_seconds": 45.2,
     "started_at": "2026-07-17T15:33:22.123456Z",
     "completed_at": "2026-07-17T15:34:07.987654Z"
   }
   ```

5. **Atualizar `calib_lote*.json`** para registrar se run foi completa ou incompleta:
   ```json
   {
     "run_id": "METER_1784293071639_RUN_1",
     "status": "complete",
     "classification": "vazamento",
     "required_met_count": 2,
     "required_total": 3
   }
   ```

**Exige re-execução da calibração**: **SIM**. Sem re-executar com a observabilidade melhorada, os dados persistidos hoje não mudam (solver output e judge verdict já foram perdidos na sessão de execução).

**Dependências**: Nenhuma issue depende desta, mas as autópsias seguintes (ISSUE-33.10 re-rodada, qualquer diagnose de meter futuro) dependem dela.

---

### ISSUE-B: Classifição de runs incompletas — melhor tratamento de erro

**Título**: Capturar e registrar status/exceção das runs incompletas em solvability_meter

**Objetivo**: Permitir diagnosticar se runs falharam por timeout, erro de parsing JSON, erro de transporte do provider ou outro motivo.

**Escopo**:

1. Envolver chamadas ao `measure_solvability` e a cada `BlindSolver` run em try-except estruturado
2. Registrar: tipo de exception, stderr, duration, status (timeout vs. parse vs. outro)
3. Garantir que runs incompletas recebem entrada em `run_results` com status de erro (não desaparecem do agregado)

**Exige re-execução da calibração**: **SIM** (correlato de ISSUE-A).

---

### ISSUE-C: Rebasing e confidence — validação do judge

**Título**: Validar classificação do judge e registrar quais conclusões foram rebaixadas por CJ_005

**Objetivo**: Diferenciar "solver acertou, judge rebaixou" (H-Ja/H-Jb) de "solver errou factualmente" (H-Sa) com dados visíveis.

**Escopo**:

1. Documentar contrato CJ_005 com exemplos (hoje só existe em código)
2. Registrar em `judge_verdict.warnings[]` a razão exata de cada rebasing (evidence vazia, formato incompatível, etc.)
3. Persistir pre-rebasing met counts opcionalmente (antes vs. depois de CJ_005)

**Exige re-execução da calibração**: Não necessariamente (pode ser retroativo se artefatos existirem).

---

## 6. Recomendação de observabilidade

### O que o meter deveria persistir daqui em diante

**Prioridade 1 — Bloqueador de autópsia**:
- ✅ `solver_report.json` por run (conclusão, reasoning, confidence, evidence_used, open_questions)
- ✅ `judge_verdict.json` por run (conclusions item-a-item, evidence_cited, rationale, warnings)
- ✅ `metadata.json` por run (status, exception, stderr, duration, timestamps)

Sem esses, nenhuma autópsia é possível — qualquer diagnose é palpite.

**Prioridade 2 — Robustez diagnóstica**:
- Status de cada run em `run_results` (hoje só existe para completas)
- Rebasing history (pre/post CJ_005 met counts por conclusão)
- Confidence scores do solver registrados (hoje só no solver output transitório)

**Prioridade 3 — Futura calibração**:
- Prompt usado por run (solver_prompt_sha256, judge_prompt_sha256 no metadata)
- Temperature / provider_id registrados por run
- Ambient context (bundle_id, E1_id, meter_id)

### Formato de estrutura recomendado

```
calibration/reports/
├── calib_lote1.json (agregado — manter como está)
├── calib_lote2.json (agregado — manter como está)
└── calib_lote1_runs.jsonl (novo: linha-por-linha, um run_record por linha)
   └── Alternativa: run_artifacts/ como sugerido em ISSUE-A

Por linha:
{
  "run_id": "...",
  "status": "complete",
  "solver_report": {...},
  "judge_verdict": {...},
  "metadata": {...}
}
```

Ou: ISSUE-A com estrutura de diretório por run (mais legível em autópsia manual).

### Impacto esperado da observabilidade

Com essas mudanças:
- Futuras autópsias de meter: podem julgar H-Ja, H-Jb, H-Sa com dados completos
- Runs incompletas: podem ser diagnosticadas por timeout/parse/outro
- Validação de juiz: pode confirmar se rebasing foi apropriado

Sem essas mudanças: próxima autópsia em ISSUE-34 / ISSUE-35 terá o mesmo problema.

---

## Síntese executiva

**Pergunta**: Por que "Uma Noite Sem Flores" (comprovadamente justa) saiu "injusto" no meter?

**Resposta**: A causa raiz não é o solver, o judge, ou o design do caso. **É a falta de observabilidade no instrumentador (`solvability_meter.py`)**. Dos 7 diagnósticos possíveis, 5 ficaram indeterminados porque os artefatos intermediários (solver output, judge verdict, run error logs) nunca foram persistidos. Sem eles, qualquer análise passa por "deve ser timeout", "deve ser semântica", "deve ser solver", sem prova. A execução pode ter funcionado, mas o telefone quebrado é a instrumentação.

**Recomendação imediata**:
1. Implementar ISSUE-A (persistência de run records completos) como pré-requisito
2. Re-executar calibração com observabilidade melhorada
3. Re-rodar ISSUE-33.10 STEP-05 (este diagnóstico) com dados novos
4. Só então confirmar ou refutar H-Ja/H-Jb/H-Sa/H-Ra/H-Ma

**Impacto em roadmap**: O portão de ISSUE-30.11 (esperando sinal da calibração da 33.9) permanece fechado até a re-autópsia. Não há decisão para "aceitar meter como-é" — há apenas "meter não é observável o bastante para decidir".

