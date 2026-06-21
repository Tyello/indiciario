# Review Report — ISSUE-21 STEP-06

STEP: STEP-06
STEP_TYPE: red
REVIEW_STATUS: approved
SEVERITY: none

## Arquivos esperados
- tests/test_narrative_reviewer.py (criado)

## Arquivos alterados encontrados
- tests/test_narrative_reviewer.py (untracked, novo)
- .ai/issues/ISSUE-21+22.md (somente bloco de estado/histórico — controle)
- .ai/runs/ISSUE-21/STEP-06_EXECUTION.md (report do executor)

Confirmado via git status --short / git diff --name-only:
- generator/narrative_reviewer.py NÃO alterado (untracked desde STEP-05; sem review_narrative).
- schemas/review_report.schema.yaml NÃO alterado (untracked desde STEP-05).
- Nenhum generator/evidence_reviewer.py criado.
- Nenhum schema novo.

## Verificações
- [x] Execution report existe
- [x] Type válido (red)
- [x] Arquivos dentro do escopo (só tests/test_narrative_reviewer.py editável)
- [x] Comandos dentro do permitido (pytest tests/test_narrative_reviewer.py -q)
- [x] Critérios de done atendidos (25 casos 21–45 presentes; RED registrado)
- [x] Critérios do tipo red atendidos (só teste criado, sem GREEN)
- [x] Sem escopo extra (nenhuma implementação, schema ou evidence_reviewer)

## Conferência específica do checklist

### Escopo red
- Só tests/test_narrative_reviewer.py criado/alterado entre arquivos de produto.
- generator/narrative_reviewer.py contém apenas dataclasses + validate_review_report + report_to_dict (STEP-05). SEM review_narrative. Confirmado por leitura direta do arquivo.
- Nenhum GREEN. Nenhum schema novo.

### Casos 21–45 (25 casos)
Presentes e contados:
- 21–28: NR_001..NR_008 (presença/ausência por code).
- 29–38: review_narrative + status + serialização + não-mutação + echo de report_id/reviewer_type/blueprint_ref.
- 39–45: validate_review_report + preservação de codes + defaults + ordenação por severidade + smoke.
RED: import `review_narrative` de generator.narrative_reviewer → ImportError (símbolo ausente). Falha de coleta pelo motivo certo, registrado no execution report.

### Campos de modelo (anti-invenção)
Conferido contra generator/models.py todas as factories:
- Personagem: id, nome, funcao, papel, suspeita_aparente, verdade, documento_ancoragem — todos reais.
- Documento: codigo, titulo, envelope, tipo, emocao_esperada, objetivo_narrativo, pistas_contidas, ids_citados, conteudo (dict) — todos reais.
- Pista: descricao, documento, o_que_sugere, o_que_prova, confirmacao, risco_ambiguidade, emocao_esperada — todos reais. SEM campo `obrigatoria` (correto; é ER_007/STEP-08, DVG-EXEC-001).
- Pilar, RedHerring, Dica, ObjetivoEnvelope, ConflitoCentral, GuiaOperacional — campos batem.
NENHUM campo de modelo inventado.

## Divergências
- DVG-EXEC-002/003 (herdadas de STEP-01) reafirmadas no report: PapelPersonagem sem literais "suspeito"/"vitima"; NR_003/NR_007 testados por comportamento via heurística de "suspeito alternativo" (red_herring/intermediario/cumplice ausente). conteudo é dict, texto interpretativo/motivação em valores do dict.
- Cobertura dedicada apenas dos codes nomeados explicitamente na spec para 21–28 (NR_001/003/004/006/008); NR_002/005/007 sem caso isolado. Coerente com a spec: os casos 21–28 nomeiam exatamente esses 8 cenários, não 8 codes distintos. Não é escopo extra nem ausência de done-when.
- Severidade: none. Divergências são de modelagem coerente com a spec, não desvios de escopo.

## Decisão
APPROVED
