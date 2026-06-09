# Prompt skill: improve-codebase-architecture

Use este prompt apenas quando houver uma rodada explícita de arquitetura. Não use durante hardening editorial, correção pontual de PDF ou preparação imediata de playtest.

## Instrução para o agente

Você está trabalhando no projeto Indiciário.
Use a abordagem `improve-codebase-architecture`.

Seu objetivo é identificar melhorias incrementais e reversíveis, sem reescrever o projeto nem abrir novas superfícies de produto.

## Processo obrigatório

1. **Ler contexto**
   - `AGENTS.md`
   - `docs/AGENT_SKILLS.md`
   - `docs/ESTADO_ATUAL.md`
   - `docs/ROADMAP.md`
   - arquivos técnicos diretamente afetados

2. **Mapear responsabilidades atuais**
   - Onde está o domínio?
   - Onde está renderização?
   - Onde está validação?
   - Onde está empacotamento?
   - Onde há acoplamento real?

3. **Identificar problemas comprovados**
   - Duplicação que causa erro.
   - Responsabilidade misturada.
   - Teste difícil por desenho ruim.
   - Fragilidade recorrente em PRs anteriores.

4. **Propor mudanças pequenas**
   - Preferir extração de função/classe bem delimitada.
   - Preferir compatibilidade com API atual.
   - Evitar migração ampla sem necessidade.

5. **Definir plano de validação**
   - Testes unitários.
   - Validators strict dos canônicos.
   - Build real se tocar renderização/pacote.

## Saída final obrigatória

No final, responda com:

- Skill usada: `improve-codebase-architecture`.
- Diagnóstico arquitetural.
- Problemas comprovados.
- Mudanças recomendadas por prioridade.
- Mudanças explicitamente não recomendadas agora.
- Plano de validação.

## Guardrails do Indiciário

- Não criar banco de dados, dashboard, marketplace, multiusuário, Telegram comercial ou IA de imagem por iniciativa própria.
- Não trocar Playwright/pikepdf sem evidência forte.
- Não reescrever o pipeline antes de baseline visual/playtest.
- Arquitetura boa é a que protege caso jogável, solvabilidade, PDF real e operação simples.
