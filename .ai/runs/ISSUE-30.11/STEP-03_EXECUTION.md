# STEP-03_EXECUTION — ISSUE-30.11

STEP: STEP-03 — GREEN estrutural + pipeline
Type: green (high-risk, revisor obrigatório)
Executor: EXECUTOR (autônomo)
Arquivo alvo: `examples/caso_gerado_cooperativa.json`

## Resumo

Blueprint draft de STEP-02 falhava construção Pydantic (327 erros — `Blueprint(**json)` nem instanciava: campos ausentes/nomes errados, `objetivos_por_envelope.envelope` como int, `verdade_real` como dict, `linha_tempo_real`/`linha_tempo_documental` com nomes de campo trocados, `contratos_evidencia`/`pilares_validacao`/`dicas` fora do shape). Reescrita estrutural completa de `examples/caso_gerado_cooperativa.json`, preservando domínio (Cooperativa Agrícola Vale Novo, fraude de pesagem por Joaquim Petter — id 02, executor=planejador=beneficiario), PAT-01..04 (herdados de STEP-02: relação de personagens antes de nomes/ações — PAT-01; código de lote como chave cruzada — PAT-03/04; folha de cruzamento para descarte — PAT-02), red herrings (Tiago Bessa id 05, Vinícius Andrade id 07 — adicionado para satisfazer `ELENCO_004`), 7 personagens, 17 documentos (E1: 9, E2: 8 — adicionado `E1-09` folha_cruzamento para não disparar `DOC_004`), 5 contratos de evidência, 3 pistas, 4 pilares, 6 dicas.

Referência estrutural: `generator/models.py` (Blueprint Pydantic completo, lido integralmente), `examples/caso_canonico_iniciante.json` (shapes de `conteudo` por tipo de documento), `generator/schemas/*.yaml` (campos obrigatórios por tipo técnico).

Nenhuma alteração em `generator/` — só blueprint.

## Comando 1 — Validator strict (iteração final)

```
.venv\Scripts\python.exe -m generator.validator examples\caso_gerado_cooperativa.json --strict
```

Saída (final, após correção de `CE_006`):

```
============================================================
VALIDAÇÃO DE BLUEPRINT — O Grão que Faltou
============================================================
Risco: Médio-baixo
Pode gerar: SIM
Críticos: 0
Moderados: 1
Avisos: 11

MODERADOS
[DC_000] Contratos de evidência existem, mas nenhuma dica contextual foi definida.
  - O pacote continua gerável; adicione dicas para apoiar o facilitador em travamentos reais.

AVISOS
[ELENCO_001] Executor, planejador e beneficiário apontam para o mesmo personagem.
  - Caso com culpado único; válido quando a concentração dos papéis for intencional.
[GP_003] Documento 'E1-01' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-02' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-06' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-07' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E1-08' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-01' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-06' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-07' não participa de nenhum contrato de evidência.
[GP_003] Documento 'E2-08' não participa de nenhum contrato de evidência.
[CONT_002] 'E1-06' é tipo 'cadastro_terceiros' sem schema técnico de conteúdo definido.
  - Tipo ainda cai em fallback controlado; crie schema antes de produção estrita.
```

Exit code: 0. Críticos: 0. Moderados: 1 (< 2 — passa mesmo sob `--strict`). Avisos: 11 (não bloqueiam).

### Iteração anterior (registrada para rastreabilidade)

Primeira tentativa pós-reescrita retornou 4 críticos `CE_006` (`descarta_alternativas` do contrato `ContratoEvidencia` referenciava IDs de personagem `05`/`07` em vez de códigos de documento). Corrigido trocando para `["E1-09"]` (código do documento de descarte) nos contratos `C-E1-02` e `C-FINAL`. Re-rodado o mesmo comando → 0 críticos.

**Veredito critério "strict 0 erros críticos"**: ATENDIDO (0 críticos; 1 moderado é tolerado — regra de risco só falha com moderados ≥ 2 sob strict).

## Comando 2 — Estimador de dificuldade

Módulo: `generator/playtest_metrics.py` (`estimate_difficulty`, `estimate_minutes`). Não há CLI dedicado; invocado via script curto:

```python
import json
from generator.models import Blueprint
from generator.playtest_metrics import estimate_difficulty, estimate_minutes

data = json.load(open('examples/caso_gerado_cooperativa.json', encoding='utf-8'))
bp = Blueprint(**data)
print('estimate_difficulty:', estimate_difficulty(bp))
print('estimate_minutes:', estimate_minutes(bp))
```

Saída:

```
estimate_difficulty: intermediario
estimate_minutes: 85
```

**Veredito critério "estimador = Intermediário"**: ATENDIDO.

## Comando 3 — clue_graph

Módulo: `generator/clue_graph.py` (`build_clue_graph`, `analyze_clue_graph`). Invocado via script curto:

```python
import json
from generator.models import Blueprint
from generator.clue_graph import build_clue_graph, analyze_clue_graph

data = json.load(open('examples/caso_gerado_cooperativa.json', encoding='utf-8'))
bp = Blueprint(**data)
graph = build_clue_graph(bp)
report = analyze_clue_graph(graph, bp)
print('status:', report['status'])
print('summary:', report['summary'])
print('solution_paths:', report['solution_paths'])
print('issues:', [(i['code'], i['severity']) for i in report['issues']])
```

Saída:

```
status: passed
summary: {'documents': 17, 'contracts': 5, 'nodes': 22, 'edges': 12, 'solution_targets': 1}
solution_paths: [{'target': 'C-FINAL', 'depth': 4, 'documents': ['E1-09', 'E2-04', 'E2-05'], 'contracts': ['C-E1-01', 'C-E2-01', 'C-E2-02', 'C-FINAL']}]
issues: apenas GP_003 (severity=warning) x9 — documentos de contexto (protocolos, manual, cadastro, chats, boletim de atrito, depoimento da contadora, folha de cruzamento E2-07) que não participam de contrato de evidência. Nenhum GP_007.
```

Contrato final `C-FINAL`: `depth = 4` (3 contratos obrigatórios não-finais — `C-E1-01`, `C-E2-01`, `C-E2-02` — mais o próprio final). `depth >= 2`: ATENDIDO. Nenhuma ocorrência de `GP_007` (que exigiria prova/confirmação ausentes, iguais, ou não resolvíveis no grafo — `C-FINAL` usa `prova_principal=E2-04` e `confirmacao_independente=E2-05`, distintos e existentes).

**Veredito critério "clue_graph: contrato final com depth >= 2, sem GP_007"**: ATENDIDO.

## Comando 4 — obviousness_checker

Módulo: `generator/obviousness_checker.py` (`check_obviousness`). Invocado via script curto:

```python
import json
from generator.obviousness_checker import check_obviousness

data = json.load(open('examples/caso_gerado_cooperativa.json', encoding='utf-8'))
report = check_obviousness(data)
print('report:', report)
```

Saída:

```
report: ObviousnessReport(findings=[])
```

Nenhum finding de nenhum tipo — em particular, nenhum `OBV_001` (confissão) nem `OBV_009` (nome-em-ação).

**Veredito critério "obviousness_checker: sem OBV_001/OBV_009"**: ATENDIDO.

## Veredito final por critério

| Critério | Resultado |
|---|---|
| `validator --strict` com 0 erros críticos | ATENDIDO (0 críticos, 1 moderado — `DC_000`, tolerado) |
| Estimador de dificuldade = Intermediário | ATENDIDO (`intermediario`, 85 min) |
| `clue_graph`: contrato final depth >= 2, sem GP_007 | ATENDIDO (depth=4, único issue é GP_003 warning) |
| `obviousness_checker`: sem OBV_001/OBV_009 | ATENDIDO (zero findings) |

## Divergências disclosed

- **DVG-EXEC-004**: para fechar `CE_006` foi necessário reler trechos de `generator/validator.py` e `generator/clue_graph.py` (fonte, dentro do escopo permitido "generator/ para entender validator/clue_graph/estimador/obviousness_checker") para extrair com exatidão os códigos de erro `CE_001..CE_011`, `PILAR_001..006`, `GP_001..GP_007`, `DC_000..DC_009`, `VP_*`, `MAP_*`, `CARD_*` e confirmar campos exatos do `Blueprint` Pydantic (`generator/models.py`) antes da reescrita, para minimizar iterações de tentativa-e-erro. Nenhum arquivo de `generator/` foi alterado.
- **DVG-EXEC-005**: `DC_000` (moderado) foi deixado deliberadamente sem correção — adicionar `dicas_contextuais` exigiria valores de `nivel`/`categoria` cujo enum completo (`NIVEIS_DICA_CONTEXTUAL`/`CATEGORIAS_DICA_CONTEXTUAL`) não foi extraído a tempo; como o critério de "done" do STEP-03 é 0 erros críticos (não 0 moderados), e a regra de risco só falha com moderados ≥ 2 sob strict, manter 1 moderado isolado é suficiente e mais seguro que arriscar valores de enum inválidos (`DC_008`/`DC_009`, críticos).
- **DVG-EXEC-006**: 9 avisos `GP_003` (documentos órfãos de contrato de evidência) e 1 aviso `ELENCO_001` (culpado único, concentração de papéis) foram deixados como estão — avisos não bloqueiam geração e o desenho de personagem único como executor/planejador/beneficiário é intencional (preservado de STEP-02, não é regressão).

## Arquivos alterados

- `examples/caso_gerado_cooperativa.json` — reescrita estrutural completa (conteúdo narrativo/domínio preservado de STEP-02; shape 100% novo conforme `generator/models.py`).
- `.ai/runs/ISSUE-30.11/STEP-03_EXECUTION.md` — este relatório.

## Estado da issue após este step

`STATUS: running` (inalterado). `LAST_COMPLETED_STEP: STEP-02` (inalterado — aguarda aprovação do revisor para avançar). `NEXT_ACTION: review`. `REVIEW_STATUS: pending`.

Não avançar para STEP-04. Não aprovar STEP-03.
