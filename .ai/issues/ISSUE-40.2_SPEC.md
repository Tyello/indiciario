# SPEC — ISSUE-40.2: Gate visual de fidelidade de fonte

## Contexto

A 40.1 corrige o estado atual, mas não impede regressão futura. O framework já tem o hábito de tratar "passa sem ter sido de fato avaliado" como classe de bug prioritária (30.6/30.7). Esta issue aplica o mesmo princípio ao domínio visual: nenhum template deve poder ser mesclado se depender silenciosamente de fallback de fonte de sistema.

## Escopo

Apenas o check de fidelidade de fonte. Outros checks visuais (camada tela/papel, brand leakage, microidentidade) são das issues 40.3/40.5/40.6 — cada um deve, quando chegar sua vez, seguir o mesmo padrão de integração ao gate estabelecido aqui.

## Passo a passo técnico

### STEP-01 — Levantamento

Ler `generator/canonical_quality_gate.py` e `generator/gate_evaluator.py` (citados no cabeçalho do diagnóstico como parte do pipeline Fase A-E já concluído). Confirmar:
- Como checks individuais são registrados (função isolada? classe? decorator?).
- Formato de saída esperado por um check (booleano + mensagem? objeto estruturado?).
- Como o run manifest agrega os resultados dos checks para o relatório final.

Não presumir a API exata sem essa leitura — o esqueleto abaixo é ilustrativo, ajuste ao padrão real encontrado.

### STEP-02 — RED

```python
# tests/test_gate_font_fidelity.py

def test_gate_currently_misses_font_fallback(tmp_path, monkeypatch):
    """
    Evidencia a lacuna: com um @font-face removido, o gate ATUAL
    (sem o check novo) não deveria acusar nada — o que é o bug.
    Depois do STEP-03, este comportamento muda: o teste seguinte
    (test_gate_catches_font_fallback) passa a ser o critério real.
    """
    # 1. Copiar document_system.css para tmp_path removendo uma regra @font-face
    # 2. Rodar o gate completo sobre um template que dependa dessa fonte
    # 3. Confirmar (hoje) que o gate passa mesmo com o fallback — RED documentado
    ...

def test_gate_catches_font_fallback(tmp_path):
    """Este é o teste que deve GREEN ao final da issue."""
    # mesma montagem acima, mas após STEP-03 o gate deve reportar falha
    # explícita nomeando template + fonte
    ...
```

### STEP-03 — GREEN

1. Reusar (ou extrair para módulo compartilhado, se ainda não estiver) o helper de "font-family computado" criado na 40.1.
2. Implementar `check_font_fidelity(rendered_templates: list) -> GateCheckResult` (ajustar assinatura ao padrão real do gate) que:
   - Para cada template renderizado, obtém as fontes declaradas (via inventário estático — reusar a lista de `tests/test_font_vendoring.py` da 40.1, ou derivar dinamicamente do CSS).
   - Compara com o font-family computado via Playwright.
   - Reporta falha por template+fonte, não um booleano agregado.
3. Registrar o check no pipeline com ID explícito (ex.: `GP_0XX_font_fidelity` — usar a próxima sigla livre no padrão real de nomenclatura do projeto, confirmar no STEP-01).
4. Garantir que o check roda como parte do `canonical_quality_gate.py` no fluxo normal (não como script avulso).

### STEP-04 — Verificação de regressão

Rodar os dois testes do STEP-02: o primeiro deve ter documentado a lacuna (histórico, pode virar teste "was_bug" ou ser removido após confirmação); o segundo deve estar GREEN.

### STEP-05 — Docs

Criar `framework/09_SISTEMA_VISUAL.md`:

```markdown
# Sistema Visual — Doutrina de Repaginação Documental

> Origem: DIAGNOSTICO_VISUAL_DOCUMENTAL.md (calibração 30.8, benchmark "Uma Noite Sem Flores"), lote de issues 40.x.

## Gate de fidelidade de fonte (ISSUE-40.2)

Todo template que declara uma `font-family` custom deve ter um `@font-face` local
correspondente em `templates/styles/document_system.css`, apontando para
`assets/fonts/`. O gate de qualidade (`GP_0XX_font_fidelity`) falha a run se o
font-family computado no render não bater com o declarado — sinal de fallback
silencioso para fonte de sistema.

<!-- Seções de Camada (40.3) e Microidentidade (40.6) serão adicionadas
     quando essas issues forem concluídas. -->
```

Adicionar, em `framework/07_PROMPT_GERADOR_DE_CASO.md`, uma linha de cross-referência apontando para este novo documento, no mesmo padrão usado para `08_MODELO_REFERENCIA.md`.

## Fora de escopo

- Checks de camada (tela vs. papel), brand leakage e microidentidade — cada issue subsequente adiciona seu próprio check a este mesmo gate, seguindo o padrão aqui estabelecido.

## Riscos / atenção do revisor

- Se o gate hoje não tiver um mecanismo de "check plugável", esta issue pode precisar de um pequeno refactor de infraestrutura do gate antes do check em si — sinalizar no PR se for o caso, não é motivo para expandir o escopo da issue sem avisar.
