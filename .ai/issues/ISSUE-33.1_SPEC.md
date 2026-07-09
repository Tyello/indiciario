# ISSUE-33.1 — Conclusion Judge: preenchimento automático de expected_conclusions

## Contexto

O Gate Evaluator (ISSUE-19+20) é o único ponto onde a solução privada encontra o output cego, mas hoje `expected_conclusions[].met` é preenchido **manualmente** — o gate valida coerência (GE_001–008), não correção. Com o solver LLM real (ISSUE-33) produzindo reports de verdade, falta o juiz que compara `BlindSolverReport` com o gabarito e preenche `met` de forma auditável.

O gabarito é prosa (`solucao_em_5_frases`, seções `solucao_final` do blueprint), então a comparação é semântica: exige um provider LLM, com veredito estruturado e determinístico nos testes via `FakeProvider`.

Origem: lacuna identificada em chat (jul/2026) durante diagnóstico da fase Provider; `docs/BLIND_SOLVER_HARNESS.md` (seção Gate Evaluator).

## Objetivo

Existir `generator/conclusion_judge.py` que recebe um `BlindSolverReport` + as conclusões esperadas do autor, chama o provider com um prompt de juiz e devolve um `JudgeVerdict` estruturado, pronto para alimentar `build_gate_evaluation` (campo `met` de cada `ExpectedConclusion` + classificação do caso).

## Fora de escopo

- Alterar o Gate Evaluator ou suas regras GE_001–008 (o juiz **alimenta** o gate, não o substitui).
- Extrair automaticamente as conclusões esperadas do blueprint (o chamador fornece a lista; extração automática é issue futura se necessária).
- Múltiplas execuções / dificuldade (ISSUE-33.2).

## Contrato / regras

Módulo novo: `generator/conclusion_judge.py`. Prompt versionado novo: `generator/prompts/conclusion_judge_v1.md` (PT-BR). Schema novo: `schemas/judge_verdict.schema.yaml` (`additionalProperties: false`).

```python
@dataclass(frozen=True)
class ExpectedConclusionInput:
    id: str            # ex: "culpado", "metodo", "motivo"
    statement: str     # afirmação do gabarito em prosa
    required: bool

def judge_conclusions(report: Mapping, expected: Sequence[ExpectedConclusionInput],
                      provider: LLMProvider, prompt_version: str = "v1",
                      max_repair_attempts: int = 1) -> JudgeVerdict: ...
```

`JudgeVerdict` (dataclass frozen, serializável e válido contra o schema):

- `verdict_id`, `report_run_id` (copiado do report), `prompt_hash`
- `conclusions`: lista de `{id, met: bool, evidence_cited: [artifact_id], rationale}` — um item por `ExpectedConclusionInput`, mesma ordem
- `alternative_solution_detected: bool` + `alternative_solution_summary: str | null` — derivado dos `open_questions` do report e da análise do juiz
- `classification`: enum `resolvido | nao_resolvido | vazamento | ambiguo`

Regras nomeadas:

| Código | Condição | Efeito |
|---|---|---|
| `CJ_001` | prompt do juiz contém: template versionado + report (conclusion, reasoning_summary, evidence_used, open_questions) + statements esperados. **Nada do blueprint além dos statements fornecidos** | por construção; teste de arquitetura |
| `CJ_002` | resposta do provider não parseia/valida contra o schema | 1 reparo; persiste → `ConclusionJudgeError` |
| `CJ_003` | todo `ExpectedConclusionInput` tem exatamente um item correspondente em `conclusions` (mesmo `id`, mesma ordem); item faltando ou extra | `ConclusionJudgeError` |
| `CJ_004` | classificação derivada, não confiada ao modelo: todos `required` met → `resolvido`; algum `required` não met e sem alternativa → `nao_resolvido`; `alternative_solution_detected` → `ambiguo`; met sem citar nenhuma das evidências marcadas como chave (quando o chamador fornecer `key_evidence_ids` opcional) → `vazamento` | derivação em Python puro, coberta por teste unitário sem provider |
| `CJ_005` | `met=true` com `evidence_cited` vazio no veredito do modelo | rebaixado para `met=false` + warning (mesmo espírito do RV_002: conclusão sem evidência não vale) |

Precedência de classificação (CJ_004): `ambiguo` > `vazamento` > `nao_resolvido` > `resolvido`.

### Template `conclusion_judge_v1.md` (conteúdo mínimo, PT-BR)

- Papel: juiz imparcial; compara a resolução de um detetive com o gabarito do autor.
- Para cada afirmação do gabarito: o report a estabelece? (`met`), com quais evidências, e por quê (rationale curto).
- Detectar se o report aponta (ou se as evidências permitem) uma solução alternativa coerente.
- Responder somente com JSON válido no schema do veredito.

## Impacto documental

- [ ] `docs/BLIND_SOLVER_HARNESS.md` — motivo: seção "Conclusion Judge (ISSUE-33.1)" ligando report → veredito → gate.
- [ ] `framework/05_CHECKLIST_SOLVABILIDADE.md` — motivo: registrar o juiz automatizado como verificação complementar (não substituta) do checklist humano.
- [ ] `docs/ROADMAP.md` — motivo: registrar 33.1 na fase Provider.
- [ ] `docs/ESTADO_ATUAL.md` — motivo: uma linha.
- [ ] `docs/INDICE_DOCUMENTACAO.md` — ✅/⏭️: novo schema é código; avaliar.

## Casos de teste (TDD)

Arquivo novo: `tests/test_conclusion_judge.py`. Provider sempre `FakeProvider`.

1. Caminho feliz: veredito válido do fake → `JudgeVerdict` com `conclusions` na ordem e ids corretos; `classification=resolvido` quando todos required met.
2. CJ_003: fake devolve veredito sem o item `motivo` → `ConclusionJudgeError`.
3. CJ_004 (unitário, sem provider): matriz de derivação — required não met → `nao_resolvido`; alternativa detectada → `ambiguo` mesmo com tudo met; `key_evidence_ids` fornecidos e nenhum citado → `vazamento`; precedência `ambiguo > vazamento`.
4. CJ_005: fake devolve `met=true` com `evidence_cited=[]` → item vira `met=false` com warning.
5. CJ_002: primeira resposta inválida + segunda válida → sucesso; duas inválidas → erro.
6. CJ_001: prompt registrado no fake contém os statements e o reasoning_summary do report, e não contém uma string sentinela do blueprint plantada fora dos statements.
7. Schema: veredito serializado valida contra `schemas/judge_verdict.schema.yaml`; campo extra é rejeitado.
8. Ponte para o gate: veredito convertido em `ExpectedConclusion(met=...)` alimenta `build_gate_evaluation` e produz evaluation válida (GE_004 dispara quando o juiz diz `met=false` em required + decision approved).

## Restrições arquiteturais

Herdar as padrão, com a mesma exceção declarada da ISSUE-33: módulo chama LLM em produção via provider injetado; testes 100% offline com FakeProvider. `additionalProperties: false` no schema novo. Sem mutação do report nem do gate. Sem duplicação de dataclasses (importa da 31/33 e do gate_evaluator). `ruff` limpo; `pytest tests/ -q` sem regressão.

## Critério de aceite

- [ ] `CJ_001`–`CJ_005` implementadas e cobertas por teste
- [ ] Derivação de classificação é Python puro testado sem provider
- [ ] Ponte veredito → `build_gate_evaluation` coberta por teste (caso 8)
- [ ] pytest tests/ -q passa sem regressão
- [ ] ruff limpo nos arquivos tocados
- [ ] impacto documental resolvido
