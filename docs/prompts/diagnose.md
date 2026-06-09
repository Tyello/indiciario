# Prompt skill: diagnose

Use este prompt quando houver bug, regressão, falha de build, problema visual, erro de PDF, comportamento inesperado do validator, pacote quebrado ou inconsistência sem causa óbvia.

## Instrução para o agente

Você está trabalhando no projeto Indiciário.
Use a abordagem `diagnose`.

Antes de alterar qualquer coisa:

1. Leia `AGENTS.md` e `docs/AGENT_SKILLS.md`.
2. Identifique o menor escopo reproduzível do problema.
3. Separe sintoma, causa provável e evidência.
4. Não refatore áreas não relacionadas.

## Processo obrigatório

1. **Reproduzir**
   - Execute o menor comando que demonstra o problema.
   - Para blueprint/caso: rode `python generator/validator.py <arquivo> --strict`.
   - Para testes: rode o teste específico antes da suíte inteira.
   - Para PDF/renderização: tente `python -m scripts.build_package ... --strict`.

2. **Formular hipóteses**
   - Liste 1 a 3 causas prováveis.
   - Aponte quais arquivos podem estar envolvidos.
   - Evite mudar código antes de confirmar a hipótese principal.

3. **Instrumentar o mínimo**
   - Use logs, asserts, testes ou inspeção de HTML/debug quando necessário.
   - Não deixe instrumentação temporária poluindo o projeto.

4. **Corrigir a menor causa comprovada**
   - Faça a menor mudança que resolve a causa.
   - Preserve contratos editoriais: documento de jogador mostra evidência bruta, não interpretação.

5. **Adicionar regressão**
   - Adicione ou ajuste teste que falharia antes da correção.
   - Para bug visual, prefira teste estrutural/HTML/SVG/manifest quando PDF real não for viável.

6. **Validar**
   - Rode teste específico.
   - Rode `pytest tests/ -q` quando viável.
   - Rode `ruff check generator/` se tocar Python.
   - Rode validator strict se tocar blueprint/caso.
   - Tente build real se tocar renderização/pacote.

## Saída final obrigatória

No final, responda com:

- Skill usada: `diagnose`.
- Sintoma confirmado.
- Causa raiz encontrada.
- Arquivos alterados.
- Teste/regressão criada.
- Comandos executados e resultados.
- Limitações de ambiente, especialmente Playwright/Chromium/CDN.
- Próximo passo somente se houver pendência real.

## Restrições do Indiciário

- Não usar PDF fake como prova de baseline visual real.
- Não transformar documento de jogador em gabarito disfarçado.
- Não abrir feature nova durante diagnóstico.
- Não reabrir decisões já estabilizadas sem evidência nova de teste, PDF ou playtest.
