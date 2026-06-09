# Prompt skill: to-prd

Use este prompt quando a tarefa for maior que uma PR pequena ou envolver nova capacidade de produto, nova biblioteca canônica, nova rotina de playtest, mudança de pipeline ou arquitetura relevante.

## Instrução para o agente

Você está trabalhando no projeto Indiciário.
Use a abordagem `to-prd`.

Não implemente ainda. Primeiro transforme a intenção em um PRD curto, verificável e alinhado ao estado atual.

## Processo obrigatório

1. **Contextualizar**
   - Leia `AGENTS.md`, `docs/AGENT_SKILLS.md`, `docs/ESTADO_ATUAL.md` e `docs/ROADMAP.md`.
   - Leia docs específicos da área afetada.

2. **Escrever PRD enxuto**
   - Objetivo.
   - Problema real que resolve.
   - Não-objetivos.
   - Usuário/uso esperado.
   - Escopo funcional.
   - Escopo técnico.
   - Critérios de aceitação.
   - Riscos e trade-offs.
   - Validações necessárias.

3. **Checar alinhamento com prioridade atual**
   - Baseline visual real e playtest continuam acima de features teóricas.
   - Não incluir marketplace, dashboard, banco, Telegram comercial, pagamento ou IA de imagem sem instrução explícita.

4. **Preparar decomposição**
   - Ao final, indique se deve seguir para `to-issues`.

## Template de saída

```md
# PRD — <nome da iniciativa>

## Objetivo

## Problema

## Não-objetivos

## Usuários / cenário de uso

## Escopo funcional

## Escopo técnico

## Critérios de aceitação

## Riscos e trade-offs

## Validação

## Sugestão de decomposição
```

## Regras específicas do Indiciário

- PRD não deve virar especificação gigantesca.
- Cada critério de aceitação deve ser testável ou verificável em PDF/playtest/docs.
- Se a iniciativa não ajuda caso, solvabilidade, diversão, facilitador, baseline ou playtest, rebaixe prioridade.
