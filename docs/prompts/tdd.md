# Prompt skill: tdd

Use este prompt quando a tarefa alterar comportamento de código, validação, schema, renderer, package builder, manifest, case kernel, case review ou regra automatizável dos casos canônicos.

## Instrução para o agente

Você está trabalhando no projeto Indiciário.
Use a abordagem `tdd`.

Antes de implementar:

1. Leia `AGENTS.md` e `docs/AGENT_SKILLS.md`.
2. Identifique a regra que precisa ser protegida.
3. Escreva ou ajuste um teste que falhe sem a mudança.
4. Só depois implemente.

## Processo obrigatório

1. **Definir comportamento esperado**
   - Escreva em uma frase qual regra deve passar a valer.
   - Exemplos:
     - “Documento de jogador não pode conter linguagem interpretativa.”
     - “Manifest deve listar apoio visual separado dos envelopes.”
     - “Validator deve bloquear override SVG absoluto.”

2. **Red**
   - Crie ou ajuste um teste que falhe pelo motivo certo.
   - Rode o teste específico e confirme a falha.
   - Não avance se o teste não falhar por causa relacionada.

3. **Green**
   - Implemente a menor mudança para passar.
   - Evite refatoração ampla.
   - Preserve compatibilidade com casos canônicos existentes.

4. **Refactor**
   - Limpe duplicações pequenas.
   - Não misture reorganização estrutural com mudança de regra editorial.

5. **Validação final**
   - Rode teste específico.
   - Rode `pytest tests/ -q` quando viável.
   - Rode `ruff check generator/` quando tocar Python.
   - Rode validator strict dos canônicos quando tocar blueprint/schema/validador.
   - Tente build real quando tocar renderização/pacote.

## Saída final obrigatória

No final, responda com:

- Skill usada: `tdd`.
- Regra protegida.
- Teste criado/alterado.
- Evidência de red/green, se disponível.
- Arquivos alterados.
- Comandos executados e resultados.
- Limitações de ambiente.

## Regras específicas do Indiciário

- Se tocar narrativa, prefira teste editorial/canônico específico.
- Se tocar HTML/SVG, teste estrutura, classes, textos proibidos e manifest.
- Se tocar PDF real, registre se Playwright/Chromium não estiver disponível.
- Não reduza a qualidade editorial para fazer teste passar.
