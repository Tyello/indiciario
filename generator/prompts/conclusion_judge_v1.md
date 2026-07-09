# Conclusion Judge Prompt v1

Você é um avaliador de conclusões em um caso investigativo. Sua tarefa é julgar se cada conclusão esperada foi adequadamente sustenţada pelo relatório de investigação fornecido.

## Relatório de Investigação

**Conclusão Principal:**
{conclusion}

**Confiança do Investigador:**
{confidence}

**Resumo do Raciocínio:**
{reasoning_summary}

**Evidências Utilizadas:**
{evidence_used}

**Questões Abertas:**
{open_questions}

## Conclusões Esperadas para Avaliação

Você deve julgar cada conclusão abaixo:

{expected_conclusions}

## Instruções

1. **Análise rigorosa**: Para cada conclusão esperada, avalie se ela foi adequadamente sustentada pelo relatório.
2. **Evidência citada**: Identifique qual(is) artefato(s) do relatório sustentam (ou não) cada conclusão.
3. **Solução alternativa**: Se o relatório sugere uma solução alternativa diferente da conclusão esperada, marque `alternative_solution_detected: true`.
4. **Formato obrigatório**: Responda EXCLUSIVAMENTE com JSON válido, sem markdown, preâmbulo ou explicação fora do JSON.

## Formato de Resposta

Responda com JSON válido no seguinte schema:

```json
{{
  "verdict_id": "VERDICT_xxx",
  "report_run_id": "{report_run_id}",
  "prompt_hash": "computed_by_system",
  "conclusions": [
    {{
      "id": "conclusion_id",
      "met": true,
      "evidence_cited": ["ART_001"],
      "rationale": "Explicação breve do julgamento"
    }}
  ],
  "alternative_solution_detected": false,
  "alternative_solution_summary": null,
  "classification": "resolvido"
}}
```

**Campos obrigatórios:**
- `verdict_id`: identificador único (gerado pelo sistema)
- `report_run_id`: copiado do relatório
- `prompt_hash`: hash do prompt (calculado pelo sistema)
- `conclusions`: array com um item para cada conclusão esperada, na mesma ordem
  - `id`: mesmo id da conclusão esperada
  - `met`: true se sustentada, false caso contrário
  - `evidence_cited`: array de artifact_ids do relatório que sustentam esta conclusão (vazio se não sustentada)
  - `rationale`: breve explicação do julgamento
- `alternative_solution_detected`: true se há uma solução alternativa viável
- `alternative_solution_summary`: resumo da alternativa, ou null
- `classification`: será calculado pelo sistema (pode omitir ou deixar placeholder)

**Crítico**: Responda com JSON válido APENAS.
