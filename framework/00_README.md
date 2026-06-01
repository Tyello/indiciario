# Framework de Criação de Mistérios Offline
**Kit completo para geração de jogos de investigação em dossiê com envelopes**
**Versão 2.0 — otimizado para uso por agente de IA**

---

## O que é este kit

Este framework define todas as regras, templates, checklists e guias necessários para criar jogos de investigação impressos no estilo dossiê com envelopes. Cada arquivo é autocontido e cross-referenciado.

O kit foi construído para que um agente de IA possa seguir os arquivos em ordem e gerar casos novos, originais, solvíveis e com qualidade visual consistente — sem furos lógicos, sem pistas insolúveis e sem depender de conhecimento externo ao material impresso.

---

## Regra de ouro

> Um bom mistério não é aquele em que a resposta é difícil porque faltam dados.
> É aquele em que a resposta estava ali o tempo todo, mas só fica óbvia depois que as pistas certas são conectadas.

---

## Dois modos de experiência

Este framework suporta dois modos. Declare o modo no início de cada caso e seja consistente.

**Modo offline puro:** toda validação é feita por cruzamento documental. O facilitador valida presencialmente. Nenhuma dependência digital é obrigatória.

**Modo híbrido:** as pistas são 100% offline, mas a validação de hipóteses e o sistema de dicas usam um canal digital (QR code, link, bot de WhatsApp ou número de telefone). O canal digital confirma ou nega hipóteses — não entrega pistas.

---

## Ordem de leitura obrigatória para o agente

Leia e internalize nesta ordem antes de gerar qualquer caso:

| # | Arquivo | O que define |
|---|---------|-------------|
| 1 | `01_PRINCIPIOS_DO_MODELO.md` | As 8 leis do jogo justo — nunca viole |
| 2 | `02_ESTRUTURA_ENVELOPES.md` | Arquitetura de envelopes, critérios de avanço |
| 3 | `03_TIPOS_DE_DOCUMENTOS.md` | Catálogo de 15 tipos com specs visuais |
| 4 | `04_DESIGN_DE_PISTAS.md` | Regras de pistas, códigos, cadeias, dificuldade |
| 5 | `05_CHECKLIST_SOLVABILIDADE.md` | Gate de qualidade — executar antes de gerar documentos |
| 6 | `06_TEMPLATE_NOVO_CASO.md` | Template de planejamento completo |
| 7 | `07_PROMPT_GERADOR_DE_CASO.md` | Prompt expandido para geração via LLM |
| 8 | `08_MODELO_REFERENCIA.md` | Padrões e anti-padrões dos casos de referência |
| 9 | `09_TEMPLATE_GABARITO.md` | Template do documento confidencial do mestre |
| 10 | `10_TEMPLATE_DICAS.md` | Template de dicas progressivas |
| 11 | `11_GUIA_DO_FACILITADOR.md` | Como conduzir a sessão |
| 12 | `12_GUIA_DE_PRODUCAO.md` | Design visual, tipografia, impressão |
| 13 | `13_CONTRATO_EVIDENCIA.md` | Contratos mínimos de prova, confirmação e fase |
| 14 | `14_GRAFO_DE_PISTAS.md` | Grafo lógico de pistas, contratos e solvabilidade estrutural |
| 15 | `15_CONTROLES_DA_LLM.md` | Guard rails da LLM e feedback estruturado para correção futura |
| 16 | `15_GUIA_DE_IMPRESSAO.md` | Regras operacionais do pacote de impressão |
| 17 | `16_GUIA_FACILITADOR.md` | Guia confidencial de condução e dicas contextuais |

---

## Descrição de cada arquivo

### `01_PRINCIPIOS_DO_MODELO.md`
Os 8 princípios que definem um mistério justo: solvabilidade, progressão, cruzamento de pistas, red herrings, cadeia causal, separação de materiais, autossuficiência offline e curva emocional. Violar qualquer princípio invalida o caso.

### `02_ESTRUTURA_ENVELOPES.md`
Modelo de 1+ envelopes como atos investigativos sequenciais. Define função narrativa de cada fase, documentos recomendados, critério de avanço, sequência sem buracos e separação entre envelopes de jogador, dicas e gabarito.

### `03_TIPOS_DE_DOCUMENTOS.md`
Catálogo de 15 tipos de documento com: função narrativa, quando usar, campos obrigatórios, especificações visuais, cuidados de design e equivalências temáticas (corporativo / museu / família / escola / pousada).

### `04_DESIGN_DE_PISTAS.md`
Como criar pistas essenciais, de suporte e red herrings. Inclui: regra de âncora de vínculo, regra de consistência de códigos, cadeias financeiras e logísticas, calibragem de dificuldade por sinais observáveis e os quatro pilares de validação.

### `05_CHECKLIST_SOLVABILIDADE.md`
Checklist completo em 11 seções com rubrica de risco (Baixo / Médio-baixo / Médio / Médio-alto / Alto). O agente não deve gerar documentos finais se o risco for Médio ou superior.

### `06_TEMPLATE_NOVO_CASO.md`
Template preenchível com 14 seções: identidade, premissa, verdade real, envelopes, elenco, linhas do tempo, matriz de pistas, red herrings, documentos (com campo de emoção), dicas, gabarito, checklist e histórico de versões.

### `07_PROMPT_GERADOR_DE_CASO.md`
Prompt expandido para uso em nova conversa. Inclui gate de qualidade, 17 entregáveis ordenados, formato de cada documento, formato de dicas e gabarito, e padrão de qualidade final.

### `08_MODELO_REFERENCIA.md`
Aprendizados dos casos de referência. Parte 1: o que funciona (narrador suspeito, fallback, planejamento anterior, terceirizados, cartões com código, documentos policiais). Parte 2: anti-padrões a evitar. Parte 3: fórmula reutilizável.

### `09_TEMPLATE_GABARITO.md`
Template do documento confidencial do facilitador/mestre com: resposta curta, papéis, linha do tempo, explicação por envelope, mapa de pistas, red herrings, travamentos esperados, respostas erradas comuns e fechamento narrativo.

### `10_TEMPLATE_DICAS.md`
Template de dicas progressivas com distinção entre fase de planejamento e fase de produção. Dicas em 4 intensidades: leve, média, forte e quase-gabarito. Inclui tabela de dicas por ponto de travamento.

### `11_GUIA_DO_FACILITADOR.md`
Como preparar, abrir, conduzir e fechar uma sessão. Inclui: quando intervir, como oferecer dicas sem spoiler, como validar hipóteses com os quatro pilares, o que fazer com grupo rápido ou travado, e como conduzir o fechamento.

### `12_GUIA_DE_PRODUCAO.md`
Guia visual completo: paletas por universo, tipografia por tipo de documento, templates de layout em ASCII para os 12 tipos principais, imperfeições intencionais, acessibilidade em P&B, guia de impressão e checklist visual.

### `13_CONTRATO_EVIDENCIA.md`
Define o contrato mínimo entre conclusão investigativa, fase, prova principal e confirmação independente. Serve como camada inicial de solvabilidade para impedir chute, spoiler fora de fase e conclusões sem prova.

### `14_GRAFO_DE_PISTAS.md`
Define o grafo lógico de documentos e contratos de evidência. Estabelece o `graph_report.json`, documentos órfãos, contratos órfãos, caminhos de solução, regras GP_001 a GP_007 e limitações da versão sem visualização.

### `15_CONTROLES_DA_LLM.md`
Define que a LLM não é fonte final de verdade, lista permissões e proibições de correção, estabelece prioridades para códigos `CONT_*`, `DOC_*`, `ENV_*`, `CE_*`, `GP_*` e `QA_*`, e orienta o uso técnico do `llm_feedback.json`.

### `15_GUIA_DE_IMPRESSAO.md`
Guia operacional do pacote final: separação entre material de jogador e facilitador, perfis econômico/padrão/premium, escala 100%, confidencialidade, mapas, cartões futuros e interpretação do `print_manifest.json`.

### `16_GUIA_FACILITADOR.md`
Guia confidencial de condução da sessão: papel do facilitador, diferença entre gabarito e guia, critérios de avanço por contratos de evidência, uso de dicas contextuais e prevenção de spoilers.

### `17_VISUAL_PROCEDURAL.md`
Define a camada de visual procedural controlado: mapas simples em SVG/HTML, cartões de personagens, cartões de locais, limites, proibições e regras de função narrativa.

### `18_PLAYTEST_E_METRICAS.md`
Define a camada analítica de playtest heurístico: métricas de documentos, envelopes, contratos, suspeitos, red herrings, carga cognitiva, tempo estimado e warnings de experiência que não bloqueiam geração.

---

## Separação obrigatória de materiais

Nunca misture no mesmo arquivo ou impressão:

| Material | Para quem | Arquivo separado? |
|----------|-----------|------------------|
| Envelope 1 — documentos do jogador | Jogadores | Sim |
| Envelope 2 — documentos do jogador | Jogadores (após E1) | Sim |
| Envelope 3 — documentos do jogador | Jogadores (após E2, se houver) | Sim |
| Folha de cruzamento | Jogadores (vai no E1) | Pode ser parte do E1 |
| Dicas progressivas | Facilitador (entrega sob demanda) | Sim |
| Gabarito do mestre | Somente facilitador | Sim |
| Blueprint / planejamento interno | Nunca entregue | Arquivo interno |

---

## Fluxo de trabalho para o agente

```
1. Receber tema, tom, dificuldade e modo de validação
2. Ler 01 a 05 (princípios, estrutura, catálogo, pistas, checklist)
3. Preencher 06_TEMPLATE_NOVO_CASO (planejamento completo)
4. Executar checklist do 05 → verificar risco
5. Se risco ≥ Médio: corrigir antes de avançar
6. Gerar documentos finais seguindo specs do 03 e 12
7. Gerar gabarito usando template do 09
8. Gerar dicas usando template do 10
9. Gerar instruções de facilitador com base no 11 e no 16
10. Verificar checklist visual do 12 e regras procedurais do 17 quando houver visual_procedural
11. Gerar pacote final com `python -m scripts.build_package <blueprint.json> --output output --strict`
12. Conferir `manifest.json`, `print_manifest.json`, `qa_report.json`, `graph_report.json`, `llm_feedback.json`, `guia_facilitador.pdf` e `guia_de_impressao.pdf`
13. Entregar arquivos separados por destino
```

---

## Convenções deste kit

- `[CAMPO]` — campo obrigatório a preencher
- `[OPCIONAL]` — campo recomendado mas não obrigatório
- `[INTERNO]` — nunca entra no material do jogador
- ❌ — anti-padrão a evitar
- ✅ — padrão correto a seguir
- 🔴 Crítico — corrigir antes de qualquer avanço
- 🟡 Moderado — corrigir antes da produção final
- 🟢 Melhoria — não bloqueia, mas eleva qualidade


## Exemplos oficiais

- `examples/showcase_tecnico.json` — fixture técnica para exercitar schemas, renderização, pacote final, QA, grafo e feedback estruturado. Use para validar cobertura técnica do pipeline.
- `examples/caso_canonico_intermediario.json` — caso canônico jogável em dificuldade intermediária, com dois envelopes, validação offline pura e foco em experiência real de investigação. Use como referência de produto para casos narrativos completos.

## Renderização técnica oficial

Playwright é o renderizador oficial de PDFs do Indiciário. Os PDFs são gerados
via Chromium a partir dos templates HTML; `generator/renderer.py` é a fonte
operacional dessa etapa.

Setup local mínimo:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

A orientação portrait/landscape será definida por template/tipo de documento. A
base técnica desta rodada inclui smoke test manual de ambas as orientações:

```bash
python -m scripts.smoke_playwright_pdf
```


## Pacote final técnico

A camada de pacote final junta os PDFs renderizados por destino e gera arquivos de
controle para produção:

- `01_envelope_1.pdf` — material do jogador do Envelope 1;
- `02_envelope_2.pdf` — material do jogador do Envelope 2, quando existir;
- `03_dicas_facilitador.pdf` — material confidencial de dicas, quando existir;
- `04_gabarito_mestre.pdf` — gabarito confidencial, quando existir;
- `NN_guia_facilitador.pdf` — guia confidencial de condução para o facilitador;
- `NN_guia_de_impressao.pdf` — guia operacional para gráfica/papelaria;
- `manifest.json` — descrição técnica do pacote e dos documentos;
- `print_manifest.json` — instruções de impressão;
- `qa_report.json` — QA técnico do pacote;
- `graph_report.json` — relatório técnico de solvabilidade estrutural por grafo de pistas;
- `llm_feedback.json` — feedback técnico estruturado para futura correção por LLM, não destinado a jogadores nem impressão.

Uso principal:

```bash
python -m scripts.build_package examples/showcase_tecnico.json --output output --strict
```

O QA e o grafo devem retornar `status: passed` antes de distribuir o pacote. O `llm_feedback.json` é artefato técnico interno para ciclos futuros de correção automática e não deve entrar no `print_manifest.json`.
