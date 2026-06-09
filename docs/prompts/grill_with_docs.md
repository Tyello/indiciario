# Prompt skill: grill-with-docs

Use este prompt antes de alterar regras editoriais, progressão de envelopes, dificuldade, dicas, guia do facilitador, mapas, documentos de jogador, pipeline de criação ou decisões de produto.

## Instrução para o agente

Você está trabalhando no projeto Indiciário.
Use a abordagem `grill-with-docs`.

Antes de propor ou implementar mudança:

1. Leia `AGENTS.md`.
2. Leia `docs/AGENT_SKILLS.md`.
3. Leia os documentos diretamente relacionados à tarefa.
4. Confronte a proposta com as diretrizes existentes.

## Documentos-base por tipo de tarefa

| Tarefa | Docs obrigatórios |
|---|---|
| Narrativa, progressão, envelopes | `docs/CASE_DESIGN_PIPELINE.md`, `docs/BLUEPRINT_AUTHORING_GUIDE.md`, `docs/DIRETRIZES_EDITORIAIS.md` |
| LLM/autoria de caso | `docs/LLM_OPERATING_MANUAL.md`, `docs/BLUEPRINT_AUTHORING_GUIDE.md` |
| Mapas/planta baixa | `docs/FLOORPLANS.md`, `docs/VISUAL_LIBRARY_2_0.md` |
| Visual/renderização | `docs/VISUAL_SYSTEM.md`, `docs/PRINTABLES.md` quando aplicável |
| Assinaturas/manuscritos | `docs/SIGNATURES_AND_HANDWRITING.md` |
| Estado/roadmap | `docs/ESTADO_ATUAL.md`, `docs/ROADMAP.md` |

## Perguntas obrigatórias

Antes de implementar, responda internamente:

1. A mudança melhora solvabilidade, diversão, clareza ou baseline visual?
2. Ela preserva offline-first e ausência de QR/app/link obrigatório?
3. Ela mantém evidência bruta nos documentos de jogador?
4. Ela evita voz do autor, dica óbvia ou gabarito disfarçado?
5. Ela respeita o papel de cada envelope?
6. Ela adiciona complexidade antes do playtest sem evidência?
7. Ela contradiz decisão já estabilizada em `AGENTS.md`?

## Processo obrigatório

1. **Ler docs relevantes**
   - Cite quais docs foram considerados no relatório final.

2. **Identificar tensão**
   - Aponte se existe conflito entre pedido, docs e estado atual.

3. **Propor menor mudança coerente**
   - Prefira mudança editorial/documental antes de refatoração.

4. **Atualizar documentação se a regra mudar**
   - Se a decisão muda regra de produto, atualize o doc correspondente.

5. **Validar**
   - Para docs-only: informe que não há teste necessário ou rode testes se o escopo pedir.
   - Para blueprint/código: rode comandos obrigatórios do `AGENTS.md`.

## Saída final obrigatória

No final, responda com:

- Skill usada: `grill-with-docs`.
- Docs consultados.
- Decisão tomada.
- Tensão ou trade-off identificado.
- Arquivos alterados.
- Validações executadas.
- Pontos que não foram alterados e por quê.

## Guardrail principal

Se a mudança parecer interessante, mas não for necessária antes de baseline visual/playtest, registre como próximo passo ou issue. Não implemente por ansiedade de produto.
