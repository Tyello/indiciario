# Prompt skill: zoom-out

Use este prompt quando o contexto estiver confuso, a tarefa parecer grande demais, o agente estiver preso em detalhe local ou houver risco de refatorar sem entender o fluxo completo.

## Instrução para o agente

Você está trabalhando no projeto Indiciário.
Use a abordagem `zoom-out`.

Antes de implementar, explique o fluxo afetado de ponta a ponta e identifique o menor ponto correto de intervenção.

## Processo obrigatório

1. **Mapear fluxo afetado**
   - Exemplo: Blueprint → validator → renderer → package builder → manifest → PDF.
   - Exemplo: Blueprint → Case Kernel → Case Review → guia do facilitador.

2. **Separar camadas**
   - Conteúdo/caso.
   - Modelo/schema.
   - Validação.
   - Renderização/template.
   - Empacotamento/PDF.
   - Documentação.

3. **Identificar ponto mínimo de mudança**
   - Onde a regra realmente pertence?
   - O problema é dado, template, validator, renderer ou documentação?

4. **Evitar solução superdimensionada**
   - Não criar arquitetura nova para problema local.
   - Não refatorar pipeline inteiro para corrigir documento isolado.

5. **Recomendar ação**
   - Sugira o menor plano executável.
   - Se for bug, encaminhe para `diagnose`.
   - Se for regra nova, encaminhe para `tdd`.
   - Se for feature grande, encaminhe para `to-prd`.

## Saída final obrigatória

No final, responda com:

- Skill usada: `zoom-out`.
- Fluxo afetado.
- Camadas envolvidas.
- Menor ponto correto de mudança.
- Risco de overengineering.
- Próxima skill recomendada, se aplicável.

## Guardrail do Indiciário

O fluxo oficial continua sendo:

```text
Blueprint
→ Case Kernel
→ Case Review
→ Visual Library / templates
→ Build Package
→ Baseline visual real
→ Playtest
→ Ajustes finos
```

Não pule direto para código quando o problema é núcleo investigativo, e não mude núcleo investigativo quando o problema é apenas layout/renderização.
