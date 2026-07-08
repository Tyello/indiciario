# Review Report — ISSUE-40.5 STEP-02

STEP: STEP-02
STEP_TYPE: red
REVIEW_STATUS: approved
SEVERITY: none

## Arquivos esperados
- tests/test_brand_isolation.py (novo)

## Arquivos alterados encontrados
- tests/test_brand_isolation.py (novo)
- .ai/runs/ISSUE-40.5/ (execution report — bookkeeping)
- .ai/issues/ISSUE-40.5.md (campos de controle + histórico — bookkeeping)

Confirmado via `git status --short` / `git diff --name-only`: nenhum template, CSS ou `generator/renderer.py` tocado.

## Verificações
- [x] Execution report existe (`.ai/runs/ISSUE-40.5/STEP-02_EXECUTION.md`)
- [x] Type válido (`red`)
- [x] Arquivos dentro do escopo (`Arquivos editáveis: tests/test_brand_isolation.py`)
- [x] Comandos dentro do permitido (`pytest tests/test_brand_isolation.py -q`)
- [x] Critérios de done atendidos: arquivo criado com os 2 testes; execution report documenta output real do pytest, incluindo qual teste nasce GREEN por desenho e qual é RED real
- [x] Critérios do tipo (`red`): só teste criado, sem GREEN misturado, teste representa comportamento ausente/guarda de regressão declarada explicitamente
- [x] Sem escopo extra: `templates/base.html`, `document_system.css`, `renderer.py` intocados

## Checklist específico do step (seção "Revisão" do STEP-02)
- [x] Teste de herança inspeciona CSS computado real via Playwright, não grep — confirmado por leitura direta de `tests/test_brand_isolation.py`: `page.evaluate` sobre `getComputedStyle` de cada elemento do `body` (`color`, `background-color`, 4x `border-*-color`) + `getComputedStyle(documentElement).getPropertyValue('--accent')`.
- [x] Parametrização cobre os 16 templates de Camada 1/2 confirmados pelo STEP-01, não lista arbitrária — `NON_LAYER0_TEMPLATES` = `PAPER_LAYER_TEMPLATES` (12) + `SCREEN_LAYER_TEMPLATES` (4), idêntica à lista de `.ai/runs/ISSUE-40.5/STEP-01_EXECUTION.md`; bate 1:1 com os 16 nomes no output do pytest.
- [x] Teste de escopo (`.camada-0`) é RED real hoje — output do pytest confirma `FAILED test_accent_variable_scoped_to_camada_0`, `AssertionError: templates/base.html: nenhum seletor .camada-0 encontrado`, consistente com `templates/base.html` ainda declarando `--accent` em `:root` (achado do STEP-01).

Teste 2 (`test_accent_variable_scoped_to_camada_0`) faz checagem estrutural sobre o texto-fonte de `base.html` (regex de seletor `.camada-0`), não sobre computed style — mas isso é o que o próprio contrato do STEP-02 pede explicitamente para esse teste (checar presença do seletor de escopo, não vazamento de herança). A cláusula "Proibido: teste tautológico" mira o teste de herança (teste 1), que usa Playwright de fato. Sem divergência.

## Divergências
- nenhuma

## Decisão
APPROVED
