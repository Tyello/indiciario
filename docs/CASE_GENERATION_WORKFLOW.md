# Fluxo de geração e validação de casos

Este documento conecta duas partes do projeto que são frequentemente confundidas:

- **`framework/`** — processo de **GERAÇÃO** de um novo caso. É um conjunto de prompts e
  templates usados em **chat com LLM** (não código executável). Ponto de entrada:
  `framework/00_README.md`. O prompt principal de geração é
  `framework/07_PROMPT_GERADOR_DE_CASO.md`.
- **`generator/`** — código Python que **VALIDA** o JSON (blueprint) resultante da geração,
  monta pacotes e roda a pipeline multiagente offline de qualidade. Não gera história nova.

Resumo: **`framework/` escreve, `generator/` checa.** Nenhuma etapa do `generator/` substitui
o teste cego humano.

## Fluxo ponta a ponta

### 1. Planejamento (framework, sem código)

- `framework/01_*`, `02_*`, `04_*`, `05_*` — princípios editoriais, dificuldade, checklist de
  solvabilidade.
- `framework/06_TEMPLATE_NOVO_CASO.md` — template de planejamento do caso antes de escrever o
  blueprint final.
- O checklist de solvabilidade em `framework/05_*` é um **gate humano**: exige que alguém
  efetivamente resolva o caso mentalmente/na mesa antes de prosseguir. Nenhuma ferramenta em
  `generator/` substitui isso.

### 2. Geração (framework, em chat)

- `framework/07_PROMPT_GERADOR_DE_CASO.md` é o prompt usado em chat com um LLM para produzir o
  blueprint JSON do caso.
- **O que NÃO valida**: o prompt não garante que o JSON gerado é estruturalmente válido. O
  campo `conteudo` é obrigatório em cada documento do blueprint, com as chaves exatas definidas
  no template — sem isso o build de PDF não renderiza o documento.
- **Gate estrutural entre Fase 1 e Fase 2**: o mesmo comando da etapa 3 abaixo
  (`python -m generator.validator <arquivo>.json --strict`) pode e deve rodar antes, sobre o
  esqueleto do blueprint — não só depois de tudo escrito. Ver
  `## GATE ESTRUTURAL — OBRIGATÓRIO ENTRE A FASE 1 E A FASE 2` em
  `framework/07_PROMPT_GERADOR_DE_CASO.md`. Mais barato corrigir a forma no esqueleto do que
  descobrir o erro depois dos 17 documentos finais escritos.

### 3. Validação estrutural/editorial (generator, código)

```bash
python -m generator.validator examples/<arquivo>.json --strict
```

- Valida famílias de regras: `PROG_` (progressão), `MAP_` (mapas), `CE_` (contratos de
  evidência), `PILAR_`, `FIN_`, `CONT_`, `RH_`, entre outras.
- **O que prova**: o blueprint é estruturalmente consistente com o schema e com guardrails
  editoriais automatizáveis (anti-obviedade, progressão, vazamento de gabarito).
- **O que NÃO prova**: que o caso é divertido, claro ou solucionável por um grupo real.

### 4. Revisão editorial pré-pacote (generator, código)

```bash
python -m scripts.case_review examples/<arquivo>.json
```

- Case Kernel + Case Review: camada de revisão editorial antes de gerar pacote visual.

### 5. Pipeline multiagente offline (generator, código Python, sem CLI dedicada)

```python
from generator.pipeline_runner import run_pipeline

result = run_pipeline("examples/<arquivo>.json", "RUN-ID-...", created_at="...")
```

Etapas internas: blind bundle → blind solver → gate evaluator → narrative/evidence reviewers →
run manifest.

**Limitações reais, não esconder:**
- o blind solver é um **stub determinístico** (`DeterministicPipelineSolver`) — não resolve o
  caso de fato, só produz output estruturalmente válido;
- `run_pipeline` **não invoca** os reviewers visual/accessibility — por isso `visual_score=0/0`
  nos relatórios gerados por essa pipeline.

### 6. Comparação de qualidade (generator, código Python)

```python
from generator.quality_comparative_reviewer import generate_quality_report

report = generate_quality_report(
    aurora_result.manifest,
    fintech_result.manifest,
    aurora_blueprint,
    fintech_blueprint,
)
```

- `compare_to_playtest` dentro deste módulo só reconhece o caso Aurora hoje — não generalizar
  essa comparação para outros casos sem checar o código.

### 7. Baseline visual real (generator, código + Playwright/Chromium)

```bash
python -m scripts.build_package examples/<arquivo>.json --output output/<nome> --strict
```

- Exige Playwright/Chromium instalado (`python -m playwright install chromium`).
- **O que prova**: o pacote renderiza de fato em PDF, sem erro de build.
- **O que NÃO prova**: qualidade de jogo. PDF fake nunca substitui esta etapa.

### 8. Playtest humano (fora do código)

- Teste cego em mesa real.
- Findings alimentam o Learning Ledger (`examples/learning/retrospective/`) como **regras
  futuras do framework**, nunca como patch cirúrgico direto no blueprint canônico.

## Tabela — etapa → comando → artefato → o que prova

| Etapa | Comando/API | Artefato de saída | O que prova |
|---|---|---|---|
| Planejamento | leitura de `framework/01,02,04,05,06` | nenhum (decisão humana) | checklist de solvabilidade cumprido |
| Geração | `framework/07_PROMPT_GERADOR_DE_CASO.md` em chat | blueprint JSON | nada por si só — precisa validar |
| Validação estrutural | `python -m generator.validator <arq>.json --strict` | relatório de erros/avisos | estrutura e guardrails automatizáveis |
| Revisão editorial | `python -m scripts.case_review <arq>.json` | relatório de revisão | consistência editorial pré-pacote |
| Pipeline multiagente | `generator.pipeline_runner.run_pipeline(...)` | run manifest, gate decision, findings | gate decision estruturalmente produzida (solver é stub) |
| Comparação de qualidade | `generator.quality_comparative_reviewer.generate_quality_report(...)` | `QualityComparativeReport` | comparação entre runs já executadas |
| Baseline visual | `python -m scripts.build_package <arq>.json --output output/<x> --strict` | PDFs reais, manifests de impressão | renderização real funciona |
| Playtest humano | mesa real, sem ferramenta | sessão registrada em `examples/learning/retrospective/` | solvabilidade e diversão reais |

## Aviso de fronteira

**APROVADO na pipeline multiagente offline significa "estruturalmente elegível", não
"canônico".** Promover um caso a canônico exige teste cego humano registrado — ver
`docs/DIFFICULTY_FRAMEWORK.md` e o Learning Ledger. Nenhum gate automatizado (incluindo o
Quality Gate de canonização) substitui essa exigência.
