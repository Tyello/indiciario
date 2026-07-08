# ISSUE-40.6 / STEP-05 — Execution Report (Executor)

Owner: executor
Type: correction (fallback de tokens de instituição)

## Objetivo

Corrigir a regressão confirmada de forma independente no STEP-04
(`.ai/runs/ISSUE-40.6/STEP-04_EXECUTION.md` e `STEP-04_REVIEW.md`):
`templates/06_log_acesso.html` (STEP-03) injeta 4 placeholders de
microidentidade institucional (`{{INST_COLOR}}`, `{{INST_FONT_DISPLAY}}`,
`{{INST_HEADER_SHAPE}}`, `{{HORA_COM_SEGUNDOS}}`) sem fallback no engine de
renderização, quebrando 5 testes que renderizam o log de acesso **sem**
contexto de instituição (o caso de todo blueprint canônico hoje).

## Causa raiz (confirmada)

`generator/renderer.py` tem dois pontos de entrada para renderização:

1. `renderizar_documento` → `_preparar_dados_documentais` (usa `setdefault`
   para vários tokens técnicos: `DOC_CONTROLE`, `NOME_CASO`, `ENVELOPE`
   etc., mas nenhum para os 4 tokens de instituição).
2. `renderizar_html` (engine de baixo nível, chamado diretamente por
   alguns testes e recursivamente para seções `{{#CHAVE}}...{{/CHAVE}}`) —
   **não passa** por `_preparar_dados_documentais`.

Um fallback só em `_preparar_dados_documentais` resolve o caminho (1) mas
não o (2) — confirmado experimentalmente: após o primeiro ajuste,
`test_renderer_engine.py::test_caso_canonico_templates_usados_renderizam_sem_placeholders_residuais`
(que chama `renderizar_html` diretamente sobre `documento["conteudo"]` do
blueprint canônico, sem passar pela preparação de dados documentais)
continuou falhando com os mesmos 4 tokens residuais.

## Mudança em `generator/renderer.py`

Extraída função `_aplicar_fallback_institucional(dados)` com os 4
`setdefault`, usando os mesmos valores neutros do reset CSS em
`templates/styles/institution_identity.css`:

```python
def _aplicar_fallback_institucional(dados: dict[str, Any]) -> dict[str, Any]:
    dados.setdefault("INST_COLOR", dados.get("INST_COLOR") or "#333")
    dados.setdefault("INST_FONT_DISPLAY", dados.get("INST_FONT_DISPLAY") or "Georgia, serif")
    dados.setdefault("INST_HEADER_SHAPE", dados.get("INST_HEADER_SHAPE") or "reto")
    dados.setdefault(
        "HORA_COM_SEGUNDOS",
        dados.get("HORA_COM_SEGUNDOS") or dados.get("HORA") or "00:00:00",
    )
    return dados
```

Chamada em dois pontos:

- Dentro de `_preparar_dados_documentais`, ao final, sobre `preparados`
  (dict já copiado de `dados`) — cobre o caminho de
  `renderizar_documento`.
- Dentro de `renderizar_html`, logo após
  `preparar_assinaturas_visuais`/`preparar_manuscritos_visuais`, sobre uma
  cópia local (`dict(dados)`) — cobre o caminho de baixo nível usado
  diretamente por testes de engine e por seções recursivas.

Como ambos os pontos operam sobre cópias (`dict(dados)` /
`preparados = dict(dados)` já existente), nenhum dicionário de entrada do
chamador é mutado in-place.

**Contrato preservado**: `setdefault` só entra quando a chave não está
presente. Quando o contexto de instituição É fornecido (caso de
`tests/test_institution_identity.py`), os valores reais (`museu_teste`,
`empresa_teste`) permanecem intactos — nenhum dos 4 `setdefault` sobrescreve
valor já presente.

Nenhum template foi tocado (`templates/06_log_acesso.html`,
`templates/manual.html`, `templates/cadastro.html` permaneceram como
estavam ao final do STEP-03/STEP-04 — a funcionalidade de microidentidade
não foi alterada, só ganhou fallback neutro).

## Comandos executados e resultados

Ambiente: `./.venv/Scripts/python.exe` (venv do projeto, Windows).

### 1. `pytest tests/test_institution_identity.py -q`

```
....                                                                     [100%]
4 passed in 2.42s
```

Contrato de microidentidade intacto (valores reais de museu_teste/
empresa_teste continuam aparecendo quando fornecidos).

### 2. `pytest tests/test_layer_rules.py -q`

```
............................                                             [100%]
28 passed in 4.80s
```

### 3. `pytest tests/test_renderer.py tests/test_renderer_engine.py tests/test_package_manifests.py -q`

```
........................................................                 [100%]
56 passed in 2.99s
```

Os 5 testes antes-falhos (confirmados no STEP-04) voltaram a passar:
- `test_package_manifests.py::test_build_package_strict_nao_gera_pdf_fake_sem_env`
- `test_renderer.py::test_caso_canonico_dicas_contextuais_aparecem_no_html_debug`
- `test_renderer.py::test_renderizar_documento_injeta_sistema_visual_em_documento_de_jogador`
- `test_renderer.py::test_renderizar_documento_usa_familia_visual_e_emissor_de_email`
- `test_renderer_engine.py::test_caso_canonico_templates_usados_renderizam_sem_placeholders_residuais`

### 4. `pytest tests/ -q` (suíte completa)

Executada 3 vezes para checar estabilidade. Resultado limpo (execução
representativa):

```
5 failed, 1441 passed, 3 skipped in 199.28s (0:03:19)
```

com as 5 falhas restritas às falhas pré-existentes de symlink no Windows
(mesma assinatura `OSError: [WinError 1314]`, sem relação com
`generator/renderer.py`, `templates/` ou institution identity):
- `test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

**Achado de robustez (não introduzido por este fix)**: em 2 das 3
execuções completas, apareceu uma 6ª falha intermitente,
`test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
(diff de `sha256` do artefato `stage=evidence_review` entre duas chamadas
de `run_pipeline` com o mesmo `created_at`). Investigado antes de assumir
como regressão desta correção:
- O fixture `minimal_blueprint_path` desse teste (via `_blueprint()` de
  `tests/test_narrative_reviewer.py`) não usa documentos de tipo log de
  acesso nem contexto de instituição — não passa por
  `_aplicar_fallback_institucional` com conteúdo diferente do que já
  passava antes desta correção.
- `git stash` (revertendo esta correção) + `pytest tests/ -q` completo
  reproduziu **9 falhas** (5 symlink + 4 `test_institution_identity.py`,
  batendo com o STEP-04) e **nenhuma** falha em
  `test_pipeline_runner.py` naquela execução — mas rodar
  `tests/test_pipeline_runner.py` isoladamente e em módulo várias vezes,
  com e sem a correção, mostrou a mesma falha aparecendo e desaparecendo
  entre execuções idênticas (mesmo código), confirmando que é
  intermitente e pré-existente, não causada por
  `_aplicar_fallback_institucional`.
- Registrar aqui para visibilidade; não faz parte do escopo desta issue
  (nenhum arquivo tocado por ISSUE-40.6 participa do fixture desse teste)
  e não bloqueia STEP-05. Recomenda-se abrir issue separada de robustez de
  teste caso volte a incomodar (hash de bundle não-determinístico entre
  chamadas com `created_at` fixo).

## Arquivos alterados

- `generator/renderer.py` (função `_aplicar_fallback_institucional` nova,
  chamada em `_preparar_dados_documentais` e em `renderizar_html`).

## Impacto documental

Nenhum documento normativo (`framework/09_SISTEMA_VISUAL.md`,
`docs/INDICE_DOCUMENTACAO.md`) precisa de atualização: STEP-05 é correção
de bug de engine (fallback ausente), não muda contrato, comportamento
visado ou API pública da microidentidade institucional descrita no
STEP-01/STEP-03. Este relatório (`STEP-05_EXECUTION.md`) é o artefato de
rastreabilidade da correção.

## Conclusão

Regressão do STEP-03/STEP-04 corrigida. Suíte completa volta ao estado
esperado: apenas as 5 falhas pré-existentes de symlink no Windows, sem
regressão nova atribuível a esta issue.
