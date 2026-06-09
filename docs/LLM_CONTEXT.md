# LLM_CONTEXT.md — Contexto operacional para agentes

Indiciário é um framework para criação de mistérios investigativos jogáveis em grupo, em formato de dossiê com envelopes, documentos, pistas, dicas, guia do facilitador e PDFs finais.

## Princípios

- Offline-first.
- Sem QR code obrigatório.
- Sem app obrigatório.
- Sem internet obrigatória.
- Sem links externos como parte da solução.
- Foco em dedução, investigação, mesa, impressão e experiência de grupo.

Slogan:

> Todo caso deixa sinais.

## Fluxo oficial

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

## Casos canônicos

1. **O Desvio da Reserva Mirante**
   - `examples/caso_canonico_iniciante.json`
   - régua Iniciante.

2. **O Último Brinde do Hotel Aurora**
   - `examples/caso_canonico_intermediario.json`
   - régua Intermediária.
   - Decisão atual: permanecer sem mapa, salvo evidência nova ou instrução explícita.

## Prioridade atual

1. Operar os casos pelo fluxo oficial.
2. Gerar baseline visual real com Playwright/Chromium.
3. Revisar PDFs, manifests e print manifests.
4. Realizar novo playtest do Intermediário.
5. Registrar travamentos, hipóteses erradas, tempo real, uso de dicas/cartões e diversão percebida.
6. Só depois decidir ajustes finos ou planejar canônico Avançado.

## Regras editoriais essenciais

1. Documento de jogador contém evidência bruta, não interpretação do autor.
2. Guia do facilitador, dicas, QA e relatórios podem explicar; documentos diegéticos não.
3. Mapas são plantas operacionais neutras, não solução visual.
4. Documento comercial deve parecer documento real, não síntese do puzzle.
5. Dicas destravam; não substituem investigação.
6. Baseline visual real exige Playwright/Chromium; PDF fake não prova qualidade visual.

## Fora de prioridade sem instrução explícita

- Marketplace.
- Dashboard web.
- Banco de dados.
- Editor visual.
- Multiusuário.
- Telegram comercial.
- Geração em massa.
- Pagamento.
- IA gerando imagens.
- Canônico Avançado antes de baseline visual e novo playtest.

## Seleção de skill

Antes de executar qualquer tarefa, consulte `.ai/skills/README.md`, escolha a skill adequada e carregue o arquivo correspondente em `.ai/skills/`.
