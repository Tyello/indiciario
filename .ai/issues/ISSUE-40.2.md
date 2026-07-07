# ISSUE-40.2 — Gate visual: detectar fallback de fonte

**Status:** especificada, pronta para execução
**Prioridade:** P0
**Depende de:** 40.1 (fontes vendorizadas + helper de font computado)
**Bloqueia:** nenhuma issue direta, mas é pré-requisito de doutrina para todo o lote (formaliza o gate visual que 40.3-40.6 vão querer reusar)

## Objetivo

40.1 resolve o problema uma vez, no momento em que foi feita. Sem um gate, nada impede que uma issue futura (ou um novo template) reintroduza a mesma falha silenciosa: fonte custom referenciada sem `@font-face` correspondente, degradando para fallback de sistema sem que ninguém perceba. Esta issue formaliza a detecção como parte permanente do pipeline de qualidade — mesma lógica de "falhas silenciosas são o risco mais caro" já aplicada nas 30.6/30.7, agora no domínio visual.

## Doc-impact declarado (STEP-05)

- Criar `framework/09_SISTEMA_VISUAL.md` — novo documento de doutrina, no mesmo espírito do `08_MODELO_REFERENCIA.md`. Nesta issue, registra apenas a regra do gate de fidelidade de fonte; será estendido nas 40.3 e 40.6 com o sistema de camadas e microidentidades.
- Cross-referenciar o novo doc a partir de `framework/07_PROMPT_GERADOR_DE_CASO.md`.

## Critério de aceite

1. O pipeline de qualidade (`canonical_quality_gate.py` ou equivalente) falha explicitamente se qualquer template renderizado usa uma fonte cujo `font-family` computado não bate com a família declarada no HTML/CSS.
2. O relatório do gate (run manifest) nomeia o template e a fonte específica que falhou — não um erro genérico.
3. Removendo deliberadamente um `@font-face` (teste de regressão), o gate falha; restaurando, o gate passa.
4. `framework/09_SISTEMA_VISUAL.md` existe e documenta a regra.

## Passos (referência para o executor)

1. STEP-01 — Ler a estrutura atual de `generator/canonical_quality_gate.py` e `generator/gate_evaluator.py` para integrar o novo check no padrão existente (nomenclatura de check IDs, formato de relatório).
2. STEP-02 — RED: teste que remove/renomeia temporariamente um `@font-face` e confirma que o gate atual (sem o check novo) passa incorretamente — evidência de que a lacuna existe hoje.
3. STEP-03 — GREEN: implementar o check reusando o helper de font computado criado na 40.1; adicionar ao pipeline com ID próprio (ex.: `GP_0XX_font_fidelity`).
4. STEP-04 — Confirmar que o teste do STEP-02 agora falha corretamente (gate pega o problema) e que o cenário normal (fontes ok) continua passando.
5. STEP-05 — Criar `framework/09_SISTEMA_VISUAL.md` e o cross-link em `framework/07`.

Ver `ISSUE-40.2_SPEC.md` para o detalhamento técnico completo.
