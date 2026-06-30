# ISSUE-30.11 — Geração-do-zero: gerar um caso novo e playtestar

## Contexto

A calibração da ISSUE-30.8 provou que o schema comporta um caso bom e que a QA não rejeita qualidade por motivo errado — mas o caso de calibração foi **transcrito** de um produto externo já validado em mesa, não **gerado**. A parte difícil (pista não óbvia mas justa, textura humana, desorientação justa, resolução merecida) já vinha pronta dos autores originais. Restou em aberto a pergunta que importa para o objetivo do projeto: **conseguimos gerar um caso novo tão bom quanto, do zero?**

Este é o gap 2. Só há uma forma honesta de respondê-lo: gerar um caso **novo** (não transcrever), passar pela pipeline já calibrada (30.7) usando os padrões agora codificados (30.10), e **playtestar com humanos** — porque o playtest é a única prova real de solvabilidade e de qualidade, e a nossa QA é, por construção, muda nas dimensões humanas/dedutivas (esse é o gap 1, que esta issue ajuda a tornar concreto via uma rubrica).

**Origem:** balanço de calibração 2026-06-29. Experimento de validação do motor de geração; o artefato gerado é experimental até ganhar promoção por playtest.

## Objetivo

Existir um caso **gerado do zero** que (a) passa no `validator --strict`, (b) é estimado no nível declarado pela pipeline, (c) é **playtestado por humanos** com uma rubrica qualitativa, e (d) é comparado ao caso de calibração num relatório que responde, com evidência, se geramos no nível da referência ou onde estão os gaps.

## Fora de escopo

- **Não** integrar LLM como gerador dentro da pipeline (continua P3; aqui a geração é feita em chat, fluxo "LLM gera o blueprint").
- **Não** promover o caso gerado a canônico nesta issue — é artefato experimental até que playtest + decisão editorial o promovam.
- **Não** transcrever nem adaptar caso externo. Tem que ser original.
- **Não** reutilizar o domínio do caso de calibração (museu/furto de arte), para não se apoiar na transcrição.

## Contrato / regras

### Geração
- **GEN-01 — Domínio novo.** Cenário fresco (ex.: clínica, redação de jornal, estaleiro, cooperativa — qualquer um distinto de museu/arte), Intermediário, dois envelopes.
- **GEN-02 — Sem fonte de transcrição.** Gerado a partir de `framework/07_PROMPT_GERADOR_DE_CASO.md` + `BLUEPRINT_AUTHORING_GUIDE.md`, sem copiar caso pronto.
- **GEN-03 — Uso deliberado de padrões.** Empregar explicitamente ao menos **dois** dos padrões codificados na ISSUE-30.10 (PAT-01 pilar de presença, PAT-02 descarte motivo-sem-oportunidade, PAT-03 pista-código offline, PAT-04 virada de envelope), declarando quais no relatório.
- **GEN-04 — Arquivo:** `examples/caso_gerado_<dominio>.json`, marcado como **experimental, não canônico**, em `observacoes_producao`.

### Rubrica de playtest (o instrumento qualitativo — semente do gap 1)
- **RUB-01** — Definir, em `docs/EXPERIMENTO_GERACAO_DO_ZERO.md`, uma rubrica que os playtesters pontuam de 1 a 5 nas quatro dimensões que a QA automática **não** mede:
  1. **Pista não óbvia mas justa** — a chave não é adivinhável de cara, mas é dedutível só com os documentos.
  2. **Textura humana dos documentos** — os textos soam escritos por pessoas reais, não por gabarito.
  3. **Desorientação justa** — os red herrings enganam sem trapacear (são descartáveis pelos documentos).
  4. **Resolução merecida** — a virada/solução recompensa o raciocínio, não chega de graça.
- **RUB-02** — Registrar também o objetivo: o grupo chegou ao suspeito (E1) e ao culpado+destino (E2)? Quantas dicas precisou? Tempo real de mesa.

### Portão humano
- **HUMAN-01** — O playtest é conduzido por humanos (Marcelo + mesa). A issue **pausa** (`NEXT_ACTION: human`) após o relatório pré-playtest e só retoma com os resultados em mãos. O orquestrador não simula nem pula o playtest.

### Relatório
- **REP-01** — `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` compara o caso gerado ao de calibração em duas faixas: (a) métricas de pipeline (strict, estimador, depth, GP_*), (b) rubrica humana (RUB-01/02).
- **REP-02 — Veredito honesto.** Responder explicitamente: geramos no nível da referência? Onde os gaps aparecem — na pista, na textura, na desorientação, na resolução? Cada gap vira recomendação (candidata a issue futura), incluindo se aponta para a necessidade de um revisor qualitativo (gap 1).

## Impacto documental
Consultar `docs/INDICE_DOCUMENTACAO.md` (gatilhos: "doc novo", "novo caso em examples/").

- [ ] `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` — **novo doc** (rubrica + relatório comparativo).
- [ ] `docs/INDICE_DOCUMENTACAO.md` — **obrigatório**: registrar o novo doc e o novo exemplo (na seção de não-canônicos criada na 30.8).
- [ ] `docs/ESTADO_ATUAL.md` — registrar o caso gerado como **experimental, não régua**; e o resultado do experimento.
- [ ] `README.md` / `AGENTS.md` / `CLAUDE.md` — roster: caso experimental não-canônico (uma linha cada ou ⏭️).
- [ ] CI: incluir o caso gerado na cobertura de `validator --strict`, **fora** da promoção canônica (espelhar o que a 30.8 fez).

## Casos de teste

Experimento; verificações objetivas + portão humano:

- `validator --strict examples/caso_gerado_<dominio>.json` → 0 erros.
- Estimador de dificuldade → nível declarado (intermediário), por profundidade (pós-30.7).
- `clue_graph`: ao menos um contrato final com `depth ≥ 2`, sem `GP_007`.
- `obviousness_checker`: sem `OBV_001`/`OBV_009` (sem confissão/nome-em-ação).
- GEN-03: ao menos dois padrões PAT declarados e rastreáveis no blueprint.
- **Playtest humano concluído** com a rubrica preenchida (HUMAN-01).
- `pytest tests/ -q` sem regressão.

## Restrições arquiteturais

Geração sem LLM-em-runtime na pipeline; sem rede; sem mudança de schema. O caso experimental não entra no Canonical Quality Gate. Pipeline-verde é **necessário, não suficiente** — o veredito é o playtest.

## Critério de aceite

- [ ] Caso gerado do zero, domínio novo, passa strict (0 erros), estimado no nível declarado.
- [ ] ≥2 padrões PAT usados deliberadamente e declarados.
- [ ] Playtest humano realizado; rubrica RUB-01/02 preenchida.
- [ ] `docs/EXPERIMENTO_GERACAO_DO_ZERO.md` com comparação pipeline + rubrica e veredito honesto (REP-02).
- [ ] Caso marcado experimental/não-canônico; fora da promoção canônica; INDICE atualizado.
- [ ] `pytest tests/ -q` sem regressão.
