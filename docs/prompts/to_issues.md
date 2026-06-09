# Prompt skill: to-issues

Use este prompt para quebrar PRD, roadmap, relatório de playtest, auditoria ou proposta grande em tarefas pequenas para Codex/agentes.

## Instrução para o agente

Você está trabalhando no projeto Indiciário.
Use a abordagem `to-issues`.

Não crie uma issue enorme. Transforme a iniciativa em tarefas verticais, pequenas e validáveis.

## Processo obrigatório

1. **Ler contexto**
   - `AGENTS.md`
   - `docs/AGENT_SKILLS.md`
   - PRD ou documento de origem da iniciativa
   - docs específicos da área afetada

2. **Separar por tipo de mudança**
   - Editorial/blueprint.
   - Validator/schema.
   - Renderer/template/PDF.
   - Manifest/build/package.
   - Documentação.
   - Testes.

3. **Gerar issues pequenas**
   - Uma issue deve ter um resultado claro.
   - Não misturar novo caso, renderer e validator na mesma issue.
   - Preferir entrega vertical com teste/regressão.

4. **Priorizar**
   - P0: bloqueia baseline/playtest ou quebra geração.
   - P1: melhora clareza/solvabilidade/facilitador com impacto direto.
   - P2: lapidação ou automação útil, mas não bloqueante.
   - P3: futuro/ideia ainda sem evidência.

## Template por issue

```md
## <Título curto>

Prioridade: P0/P1/P2/P3
Tipo: editorial | validator | renderer | package | docs | test | architecture

### Objetivo

### Escopo

### Fora de escopo

### Critérios de aceitação

### Validação sugerida

### Arquivos prováveis
```

## Regras específicas do Indiciário

- Cada issue deve proteger a experiência offline-first.
- Cada issue que tocar jogador deve preservar evidência bruta sem interpretação do autor.
- Tarefas de PDF devem mencionar build real com Playwright/Chromium.
- Issues P0/P1 devem ter validação objetiva.
