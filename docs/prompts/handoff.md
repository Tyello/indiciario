# Prompt skill: handoff

Use este prompt ao encerrar uma rodada de trabalho, passar contexto para outro agente ou registrar estado seguro após uma PR, investigação ou tentativa de build.

## Instrução para o agente

Você está trabalhando no projeto Indiciário.
Use a abordagem `handoff`.

Seu objetivo é deixar o próximo agente produtivo sem precisar redescobrir decisões, falhas e validações.

## Processo obrigatório

1. **Resumir objetivo original**
   - O que foi pedido?
   - Qual era o resultado esperado?

2. **Registrar estado atual**
   - O que foi concluído?
   - O que ficou pendente?
   - O que foi explicitamente descartado?

3. **Listar arquivos alterados**
   - Agrupe por docs, código, templates, examples e tests.

4. **Registrar decisões**
   - Decisões editoriais.
   - Decisões técnicas.
   - Trade-offs assumidos.

5. **Registrar validações**
   - Comandos executados.
   - Resultado exato quando disponível.
   - Falhas de ambiente.

6. **Indicar próximo passo**
   - Um único próximo passo recomendado.
   - Não abrir roadmap paralelo sem necessidade.

## Template de saída

```md
# Handoff — <título>

## Objetivo original

## Estado atual

## Arquivos alterados

## Decisões tomadas

## Validações executadas

## Limitações / falhas de ambiente

## Pendências reais

## Próximo passo recomendado
```

## Regras específicas do Indiciário

- Nunca esconda falha de Playwright/Chromium, build PDF, validator ou teste.
- Se usou PDF fake, diga explicitamente que não prova baseline visual real.
- Se a mudança foi docs-only, diga que testes não foram necessários ou não foram executados por esse motivo.
- Diferencie pendência real de ideia futura.
