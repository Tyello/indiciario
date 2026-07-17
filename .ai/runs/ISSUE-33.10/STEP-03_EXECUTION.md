# ISSUE-33.10 — STEP-03: Autópsia de run vazamento `METER_1784293071639_RUN_1`

## 1. Transcrição bruta do run extraída de `calibration/reports/calib_lote1.json`

### Dados disponíveis para `METER_1784293071639_RUN_1`

```json
{
  "run_id": "METER_1784293071639_RUN_1",
  "classification": "vazamento",
  "required_met_count": 2,
  "required_total": 3
}
```

**Interpretação**: A run foi classificada como "vazamento" (solver atingiu conclusão, mas judge descartou por falta de citação de evidência). Das 3 conclusões esperadas (culpado, método, motivo), 2 foram marcadas como `met=true` mas sem evidência formal citada.

### Achado de observabilidade: dados críticos faltantes

| Campo esperado | Localização em schema | Persistido em calib_lote1.json? | Status |
|---|---|---|---|
| `solver_run_id` | judge_verdict.report_run_id | ❌ Não | FALTANTE |
| `solver conclusion (texto)` | (não está em judge_verdict.schema) | ❌ Não | FALTANTE — seria `report.conclusion` do solver |
| `conclusions[].met` (item-a-item) | judge_verdict.conclusions[].met | ❌ Não | FALTANTE — crítico para H-Ja/Jb |
| `conclusions[].evidence_cited` | judge_verdict.conclusions[].evidence_cited | ❌ Não | FALTANTE — crítico para H-Jb |
| `conclusions[].rationale` | judge_verdict.conclusions[].rationale | ❌ Não | FALTANTE — crítico para H-Ja |
| `alternative_solution_detected` | judge_verdict.alternative_solution_detected | ❌ Não | FALTANTE |
| Solver output (JSON completo) | — | ❌ Não | FALTANTE |
| Judge verdict (JSON completo) | — | ❌ Não | FALTANTE |

**Conclusão**: O arquivo `calib_lote1.json` contém apenas agregados de nível de run (classification, met counts), não os outputs individuais de solver e judge. Sem eles, não é possível fazer diagnose em H-Ja/Jb/Sa.

---

## 2. Julgamento de H-Ja: "Judge rebaixa `met` por falha de semântica em PT"

**Esperado**: Solver acerta em prosa, mas judge marca `not_met` por paráfrase legítima não reconhecida.

**Dados necessários para julgar**:
- `solver conclusion` (prosa do solver sobre culpado/método/motivo)
- `judge_verdict.conclusions[*].met` (veredito item-a-item)
- `judge_verdict.conclusions[*].rationale` (justificativa do judge)

**Status**: ❌ **INDETERMINADA** — faltam dados

**Evidência**: `calib_lote1.json` não contém `conclusions[]` array nem `rationale`. Sem a prosa do solver e o veredito racional do judge, não é possível comparar se houve rebaixamento por semântica legítima.

**Observação**: Se H-Ja fosse a causa, esperaríamos ver no warnings do judge (`classification=vazamento` com `warnings[]` contendo "Conclusion X claimed met=true but..." por CJ_005). Não temos acesso aos warnings.

---

## 3. Julgamento de H-Jb: "CJ_005 rebaixa em massa: evidence_cited vazio"

**Esperado**: Solver conclui (met=true), mas não cita evidência formal → CJ_005 rebasa para met=false.

**Contratos relevantes**:
- `CJ_005`: "met=true com evidence_cited vazio → rebase to met=false + warning" (generator/conclusion_judge.py linhas 171–185)
- `judge_verdict.schema.yaml`: conclusões devem ter `evidence_cited: array[string]`, pode ser vazio por construção

**Dados necessários para julgar**:
- `judge_verdict.conclusions[*].evidence_cited` (lista de artifact IDs citados)
- `judge_verdict.conclusions[*].met` (pré-rebasing, se disponível)
- `judge_verdict.warnings[]` (se contém "rebased to met=false")

**Status**: ❌ **INDETERMINADA** — faltam dados

**Evidência**: 
- `calib_lote1.json` não contém `conclusions[]` array
- Contagem agregada ("required_met_count: 2 de 3") é consistente com "2 de 3 met=true", mas:
  - Sem ver `evidence_cited[]` por item, não dá contar quantos tiveram rebase por CJ_005
  - Sem ver os `warnings[]`, não dá verificar se rebase foi de fato aplicado

**Achado correlato**: Se RUN_1 teve "vazamento" com required_met_count=2, a lógica foi:
1. Solver propôs 3 conclusões
2. Judge avaliou: 2 com met=true, 1 com met=false (ou similar)
3. Medidor: detectou que 2 ≥ 3/2 (50%), mas classificou como "vazamento" por outra regra

Sem os dados individuais, não dá distinguir se o "2/3" é pré-CJ_005 (solver errou mesmo) ou pós-CJ_005 (judge rebaixou).

---

## 4. Julgamento de H-Sa: "Solver realmente errou culpado/método"

**Esperado (se H-Ja/Jb descartadas)**: Solver propõe culpado/método diferente do gabarito, não por forma/paráfrase, mas por divergência factual.

**Dados necessários**:
- `solver_report.conclusion` (prosa: "culpado é X", "método é Y")
- Comparar com `examples/caso_referencia_uma_noite_sem_flores.json` (gabarito transcrito)

**Status**: ❌ **INDETERMINADA** — faltam dados + condição de teste não atendida

**Razão dupla**:
1. Faltam solver output JSON — não temos acesso à prosa do solver
2. **Regra anti-viés**: "H-Sa só pode ser concluída depois de H-Ja e H-Jb descartadas com evidência". Mas não dá descartar H-Ja/Jb sem dados, portanto não dá nem começar H-Sa.

**Sequência correta**: Como H-Ja e H-Jb não puderam ser julgadas (falta de dados), a corrente de julgamento para. Não há base para concluir se solver errou ou judge rebaixou.

---

## 5. Síntese: por que RUN_1 foi marcada "vazamento"?

Sem os artefatos persistidos (solver output + judge verdict JSON), é impossível determinar com precisão qual camada causou o "vazamento":

| Hipótese | Evidência | Veredito |
|---|---|---|
| H-Ja | Falta: rationale do judge, conclusões item-a-item | **INDETERMINADA** por falta de judge verdict |
| H-Jb | Falta: evidence_cited por conclusão, warnings de CJ_005 | **INDETERMINADA** por falta de judge verdict |
| H-Sa | Falta: solver output; condição anti-viés (H-Ja/Jb primeiro) | **INDETERMINADA** por falta de solver output + bloqueio de ordem |

**Consequência**: O achado principal de observabilidade é que o meter não persistiu os run records individuais (solver output JSON + judge verdict JSON). Sem eles, qualquer autópsia fica congelada.

---

## 6. Recomendação imediata para observabilidade

Para que a próxima autópsia não dependa de sorte, o solvability_meter deve:

1. **Persistir solver report JSON completo** para cada run:
   ```json
   {
     "solver_run_id": "METER_..._RUN_...",
     "conclusion": "...",
     "reasoning_summary": "...",
     "confidence": "...",
     "evidence_used": [...],
     "open_questions": [...]
   }
   ```

2. **Persistir judge verdict JSON completo** para cada run:
   ```json
   {
     "verdict_id": "...",
     "report_run_id": "METER_..._RUN_...",
     "conclusions": [
       { "id": "culpado", "met": true/false, "evidence_cited": [...], "rationale": "..." },
       ...
     ],
     "classification": "...",
     "warnings": [...]
   }
   ```

3. **Persistir artefatos em diretório separado** por run_id:
   ```
   calibration/run_artifacts/
     ├── METER_1784293071639_RUN_0/
     │   ├── solver_report.json
     │   └── judge_verdict.json
     ├── METER_1784293071639_RUN_1/
     │   ├── solver_report.json
     │   └── judge_verdict.json
     └── ...
   ```

Isso permitirá futuras autópsias acessarem dados completos sem re-executar.

---

## 7. Status final para STEP-03

- **H-Ja**: INDETERMINADA (faltam dados: judge verdict)
- **H-Jb**: INDETERMINADA (faltam dados: judge verdict, evidence_cited)
- **H-Sa**: INDETERMINADA (faltam dados: solver output + bloqueio de ordem)
- **Achado crítico**: Observabilidade insuficiente — artefatos de run não foram persistidos
- **Impacto**: A diagnose não pode prosseguir sem re-execução ou recuperação de dados

**Próximos steps**:
- STEP-04: Tentar julgar H-Ra/H-Ma (runs incompletas + ambiguidade) com dados que podem estar disponíveis
- STEP-05: Compilar diagnóstico final com conclusões sobre observabilidade e propor issue de melhoria no meter

**Observação de procedimento**: Este step seguiu a spec (investigação forense, leitura de calib_lote1.json, registro de indeterminações). Nenhum gatilho de escalação disparou (nenhuma decisão residual, nenhuma impossibilidade estrutural — apenas insuficiência de dados, que é um achado autorizado).
