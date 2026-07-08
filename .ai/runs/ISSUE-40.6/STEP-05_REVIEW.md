# ISSUE-40.6 / STEP-05 — Review Report (Revisor)

Owner: revisor (independente do executor)
Type: correction (fallback de tokens de instituição)

## Objetivo da revisão

Confirmar de forma independente que a correção do STEP-05
(`.ai/runs/ISSUE-40.6/STEP-05_EXECUTION.md`) resolve a regressão do
STEP-04 sem quebrar o contrato de `tests/test_institution_identity.py`
(STEP-02/03) e sem sair do escopo permitido pela issue.

## 1. Leitura da mudança em `generator/renderer.py`

`git diff -- generator/renderer.py` mostra hunks em duas categorias:

- **Pré-existentes do STEP-01/03** (não é objeto desta revisão, já
  presentes antes do STEP-05): `INSTITUTION_IDENTITY_CSS_PATH`,
  adição de `manual.html`/`cadastro.html` a `DOCUMENT_PLAYER_TEMPLATES`,
  `TEMPLATE_DOCUMENT_CLASS`, `TEMPLATE_LAYER_PAPER`,
  `DOCUMENT_TYPE_FAMILIES`, função `_institution_identity_css()`, e a
  promoção `ASSINATURA_RESPONSAVEL_NOME` → `ASSINATURA_RESPONSAVEL`.
- **Objeto do STEP-05** (confirmado contra o relatório do executor,
  linha a linha):
  - `preparados = _aplicar_fallback_institucional(preparados)` ao final
    de `_preparar_dados_documentais`.
  - Nova função `_aplicar_fallback_institucional(dados)`:
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
  - `dados = _aplicar_fallback_institucional(dict(dados))` dentro de
    `renderizar_html`, logo após `preparar_assinaturas_visuais`/
    `preparar_manuscritos_visuais`.

**Avaliação**: mudança é puramente aditiva. Usa `setdefault`, que só
insere quando a chave está ausente — nunca sobrescreve valor já
presente no dict (mesmo padrão já usado para `DOC_CONTROLE`,
`NOME_CASO`, `ENVELOPE` no mesmo arquivo). Não reescreve nem remove
lógica existente. Os dois pontos de chamada operam sobre cópias
(`preparados` já é cópia em `_preparar_dados_documentais`; `dict(dados)`
em `renderizar_html`), então nenhum dict do chamador é mutado in-place
— consistente com o alegado.

Valores de fallback batem exatamente com o reset neutro de
`templates/styles/institution_identity.css`:
`--inst-color: #333`, `--inst-font-display: Georgia, serif`,
`--inst-header-shape: reto`. `HORA_COM_SEGUNDOS` cai para `HORA` (se
disponível) ou `"00:00:00"` — razoável, mantém formato de hora válido
sem inventar um valor fora do domínio esperado pelo template.

**Observação menor (não bloqueante)**: o padrão
`dados.setdefault(K, dados.get(K) or fallback)` é redundante — como
`setdefault` só age quando a chave está ausente, o `dados.get(K)` do
segundo argumento é sempre `None` nesse caso, então o `or fallback`
sempre vence. Se a chave estiver presente mas com valor falsy
(`""`/`None` explícito), `setdefault` não substitui — mas isso não
gera `PlaceholderResidualError` (só chave *ausente* deixa `{{TOKEN}}`
literal no HTML), então não é bug funcional para o escopo desta issue.
Vale simplificar para `dados.setdefault(K, fallback)` num passe de
limpeza futuro, sem urgência.

## 2. Testes-alvo (rodados pelo revisor)

```
pytest tests/test_institution_identity.py -q
....                                                                     [100%]
4 passed in 2.31s

pytest tests/test_layer_rules.py -q
............................                                             [100%]
28 passed in 4.75s

pytest tests/test_renderer.py tests/test_renderer_engine.py tests/test_package_manifests.py -q
........................................................                 [100%]
56 passed in 2.98s
```

Os 5 testes antes-falhos (confirmados no STEP-04) fazem parte deste
conjunto e passam. Contrato de `test_institution_identity.py` intacto
(4/4), sem regressão nos valores reais quando contexto de instituição
é fornecido.

## 3. Suíte completa (2 execuções independentes)

**Execução 1**:
```
5 failed, 1441 passed, 3 skipped in 200.68s
```
5 falhas = exatamente as pré-existentes de symlink Windows
(`OSError: [WinError 1314]`):
- `test_blind_bundle_generator.py::test_symlink_source_is_rejected_and_not_followed`
- `test_blind_bundle_leak_checker.py::test_symlink_inside_bundle_fails`
- `test_blind_bundle_leak_checker.py::test_symlink_manifest_fails`
- `test_blind_bundle_leak_checker.py::test_bundle_path_missing_file_and_symlink_fail`
- `test_blind_bundle_sanitizer.py::test_source_symlink_invalid_manifest_hash_mismatch_and_undeclared_file_fail`

Sem sinal do flake `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
nesta execução — bate com o "Done quando" da issue (volta a 5
failed/1441 passed).

**Execução 2**:
```
5 failed, 1441 passed, 3 skipped in 197.86s
```
Mesmas 5 falhas de symlink Windows, mesma contagem de passed/skipped.
Sem sinal do flake também nesta segunda execução independente.

### Investigação do flake relatado pelo executor

Lido `tests/test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
(linha 332) e a fixture `minimal_blueprint_path` (linha 65, via
`_write_minimal_blueprint` → `minimal_blueprint()` de
`tests/test_narrative_reviewer.py::_blueprint`, linha 245). O blueprint
mínimo usado por esse teste é genérico (focado em regras
NR_001–NR_008 de revisão narrativa) e não contém documento do tipo log
de acesso nem contexto de instituição — nenhuma chave `INST_*` ou
`HORA_COM_SEGUNDOS` é exercitada por esse fixture. Não há caminho
plausível de `_aplicar_fallback_institucional` (que só toca essas 4
chaves específicas) influenciar o hash SHA-256 do artefato
`evidence_review` comparado nesse teste.

Concordo com a análise do executor: é não-determinismo pré-existente
do `pipeline_runner`/hash de artefato, não relacionado a esta issue.
Fica como item de acompanhamento separado (robustez de teste), não
bloqueia STEP-05.

## 4. Escopo de arquivos tocados

```
git diff --stat
 .ai/issues/ISSUE-40.6.md     | 281 ++++++++++++++++++++++++++++++++++++++++++-
 generator/renderer.py        |  53 +++++++-
 templates/06_log_acesso.html |  10 +-
 3 files changed, 336 insertions(+), 8 deletions(-)
```

`generator/renderer.py` é o único arquivo de produção com mudança
atribuível ao STEP-05 (confirmado linha a linha na seção 1).
`templates/06_log_acesso.html` já estava modificado desde o STEP-03
(nenhuma edição nova de template neste passo, conforme relatado pelo
executor e consistente com "Nenhum template foi tocado" — o trabalho
desta issue não é commitado por step, então o diff acumulado é
esperado). Nenhum arquivo fora do permitido (`Arquivos editáveis` do
STEP-05: `generator/renderer.py` e, se necessário, os 3 templates) foi
tocado.

## Veredito

**Aprovado.**

- Regressão do STEP-04 corrigida: os 5 testes voltam a passar, suíte
  completa volta ao baseline esperado (5 failed pré-existentes de
  symlink Windows, 1441 passed, 3 skipped).
- Contrato do STEP-02/03 preservado: `test_institution_identity.py`
  segue 4/4, sem sobrescrever valores reais de instituição.
- Mudança é estritamente aditiva (`setdefault`), escopo restrito a
  `generator/renderer.py`, sem tocar templates ou testes fora do
  permitido.
- Flake intermitente de `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
  investigado e confirmado não-relacionado (fixture não exercita
  nenhuma chave `INST_*`/`HORA_COM_SEGUNDOS`); não bloqueia esta issue.

## Recomendação para o orquestrador

- **Avançar para STEP-06 (docs)**.
- Abrir item de acompanhamento separado (fora do escopo da ISSUE-40.6)
  para o não-determinismo intermitente de
  `test_pipeline_runner.py::test_run_pipeline_is_deterministic_with_same_created_at`
  (hash de artefato `evidence_review` variando entre chamadas com
  `created_at` fixo) — não é regressão desta issue, mas é um sinal de
  robustez de teste que merece triagem própria.
- Nota menor de limpeza (não bloqueante, pode entrar em STEP-06 ou
  ficar para depois): simplificar
  `dados.setdefault(K, dados.get(K) or fallback)` para
  `dados.setdefault(K, fallback)` em `_aplicar_fallback_institucional`
  — comportamento idêntico, código mais direto.
