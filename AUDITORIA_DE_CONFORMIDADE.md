# Indiciário — Auditoria de Conformidade do Framework

Data da auditoria: 2026-06-06

## 0. Escopo, método e comandos de evidência

Esta auditoria verifica se o estado real do repositório corresponde ao que a documentação afirma existir. A análise é conservadora e baseada exclusivamente em evidências locais do repositório e nos comandos executados durante a auditoria.

Critérios usados:

- **IMPLEMENTADO**: há arquivos, funções, templates, modelos, validações e/ou saída gerada que comprovam a funcionalidade.
- **PARCIALMENTE IMPLEMENTADO**: há implementação real, mas com lacunas operacionais, cobertura limitada ou dependência de revisão manual.
- **NÃO IMPLEMENTADO**: não há prova de implementação no repositório.
- **IMPLEMENTADO MAS DIFERENTE DO DOCUMENTADO**: há implementação real, mas ela diverge de documentação/instrução vigente.
- **PENDÊNCIA OPERACIONAL**: o código existe, mas falta execução/revisão real de baseline visual com Playwright/Chromium.

Comandos usados como evidência:

```bash
rg --files -g 'AGENTS.md' -g 'README.md' -g 'docs/*.md' -g 'examples/*.json' | sort
rg -n "class |def |playwright|pikepdf|pypdf|manifest|print_manifest|printable|floorplan|landscape|signature|rubrica|assinatura|manuscrito|conflito_central|objetivos_por_envelope|contratos_evidencia|guia_operacional|dicas_contextuais|visual_procedural|obvious|anti|documento.*resolve|soluciona|Hotel Aurora|Último Brinde|mapa" generator scripts templates tests examples docs/ESTADO_ATUAL.md docs/ROADMAP.md README.md
python generator/validator.py examples/caso_canonico_iniciante.json --strict
python generator/validator.py examples/caso_canonico_intermediario.json --strict
python -m scripts.build_package examples/caso_canonico_iniciante.json --output /tmp/indiciario_audit_output --strict
python -m playwright install chromium
INDICIARIO_ALLOW_FAKE_PDF=1 python -m scripts.build_package examples/caso_canonico_iniciante.json --output /tmp/indiciario_audit_fake --strict
INDICIARIO_ALLOW_FAKE_PDF=1 python -m scripts.build_package examples/caso_canonico_intermediario.json --output /tmp/indiciario_audit_fake --strict
find . -maxdepth 4 \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o -iname '*.pdf' \) | sort
find output -maxdepth 3 -type f \( -name '*.pdf' -o -name '*.png' -o -name '*.json' \) -printf '%TY-%Tm-%Td %TH:%TM %p\n' | sort
```

### Resultados operacionais observados

- `python generator/validator.py examples/caso_canonico_iniciante.json --strict`: passou com risco baixo, 0 críticos, 0 moderados e 12 avisos.
- `python generator/validator.py examples/caso_canonico_intermediario.json --strict`: passou com risco baixo, 0 críticos, 0 moderados e 7 avisos.
- Build real do Iniciante sem fake PDF falhou por ausência do executável Chromium local do Playwright.
- `python -m playwright install chromium` falhou por HTTP 403 no download do Chromium.
- Build fake com `INDICIARIO_ALLOW_FAKE_PDF=1` passou para os dois canônicos, gerando PDFs sintéticos, manifests, print manifests, QA, graph, LLM feedback e playtest report.

> Observação: builds fake comprovam a orquestração do pipeline e a criação de arquivos esperados, mas **não** comprovam renderização visual real nem layout final via Chromium.

---

## 1. Resumo Executivo

| Categoria | Quantidade |
|---|---:|
| Implementado | 12 |
| Parcialmente implementado | 6 |
| Não implementado | 1 |
| Implementado mas diferente do documentado | 1 |
| Pendência operacional | 2 |

### Leitura geral

O framework está tecnicamente funcional no nível de código: há modelos Pydantic para blueprint, schemas YAML, validator strict, renderer HTML/PDF via Playwright, package builder, merge com `pikepdf` e fallback `pypdf`, manifests, printables, mapas procedurais, assinaturas/rubricas/manuscritos, guia do facilitador, dicas contextuais, QA e grafo de pistas.

A principal lacuna comprovada não é ausência de código, mas **pendência operacional de baseline visual real**: o ambiente auditado não possui Chromium instalado e o download via Playwright retornou 403. A própria documentação já trata esse baseline como próximo passo, não como fase concluída.

A divergência crítica de documentação é interna: o `AGENTS.md` do repositório declara apenas o Mirante como canônico atual e diz para não referenciar `caso_canonico_intermediario.json` salvo pedido explícito, enquanto `docs/ESTADO_ATUAL.md`, `docs/ROADMAP.md`, os playtests e o próprio arquivo `examples/caso_canonico_intermediario.json` consolidam o Hotel Aurora como régua canônica Intermediária validada.

---

## 2. Matriz de Conformidade

| Área | Status | Evidência | Observação |
|---|---|---|---|
| Blueprint JSON | IMPLEMENTADO | `generator/models.py` define `Blueprint` com campos estruturais obrigatórios, documentos, dicas, contratos, visual procedural e printables. `examples/caso_canonico_iniciante.json` e `examples/caso_canonico_intermediario.json` existem e carregam no validator strict. | Os dois canônicos validaram sem críticos/moderados. |
| Schemas YAML | IMPLEMENTADO | `generator/schema_loader.py` carrega schemas; `generator/schemas/*.yaml` existe; validator chama `load_all_schemas()` e valida conteúdo por tipo. | Há testes dedicados de schema loader e validator. |
| Validator | IMPLEMENTADO | `generator/validator.py` executa verificações de elenco, documentos, progressão, contratos, grafo, dicas, visual procedural, printables, autossuficiência, schemas, manuscritos e anti-obviedade. | Strict dos dois canônicos passou com avisos. |
| Package builder | IMPLEMENTADO | `generator/package_builder.py` orquestra validação, renderização, visuais, merge, printables, manifests, guia do facilitador, guia de impressão, QA, graph, playtest e feedback LLM. `scripts/build_package.py` expõe CLI. | Build fake ponta a ponta passou para os dois canônicos. |
| Renderização HTML | IMPLEMENTADO | `generator/renderer.py` injeta CSS documental, classes, cabeçalho/rodapé, processa templates Mustache-like e salva HTML debug quando solicitado. | HTML debug foi gerado no build fake. |
| Renderização PDF / Playwright | PARCIALMENTE IMPLEMENTADO | `generator/renderer.py` usa `playwright.async_api.async_playwright`, `chromium.launch()` e `page.pdf(format="A4", print_background=True, landscape=...)`. | Código existe; execução real falhou no ambiente por Chromium ausente. |
| Merge PDF | IMPLEMENTADO | `generator/merger.py` usa `pikepdf` quando disponível e fallback `pypdf`; valida contagem de páginas após merge. | Está alinhado à documentação de `pikepdf` oficial e `pypdf` fallback. |
| `manifest.json` | IMPLEMENTADO | `generator/package_builder.py` escreve manifest com `case`, `files`, `documents`, `printables`, `reports` e warnings. Build fake gerou `manifest.json` nos dois canônicos. | Manifest inclui printables como `printable_support` em `files` e também em `printables`. |
| `print_manifest.json` | IMPLEMENTADO | `generator/print_guide.py` cria print manifest a partir do manifest, com orientação, papel, destino e instruções. Build fake gerou `print_manifest.json`. | `visual_support_files` separa apoio visual/printables de `player_files`. |
| Sistema visual P0 | IMPLEMENTADO | `templates/styles/document_system.css` contém tokens CSS, famílias documentais, carimbos, tabelas P&B e estilos de facilitador; `generator/renderer.py` injeta CSS e classes por tipo/família. | Implementação real, não apenas documentação. |
| Cabeçalhos e rodapés documentais | IMPLEMENTADO | `generator/renderer.py` define `_documento_stamped_header_footer()`, `_documento_footer()` e injeta em templates de jogador. | Aplicado apenas aos templates em `DOCUMENT_PLAYER_TEMPLATES`. |
| Diferenciação jogador/facilitador | IMPLEMENTADO | `generator/renderer.py` adiciona `doc-player` para templates de jogador e `facilitator-doc` para família facilitador; CSS marca facilitador como confidencial. Manifest também separa categorias `player`, `facilitator`, `production`, `printable_support`. | Diferenciação existe em HTML/CSS e no pacote. |
| Printables P1 | IMPLEMENTADO | `generator/models.py` define `PrintableCard`; `generator/printable_cards.py` gera folhas por tipo em `printables/`; `templates/printable_cards.html` existe. | Build fake gerou cartões de personagem/local/objeto no Mirante e personagem/local no Aurora. Aurora não possui cartões de objeto no blueprint, portanto não gera `cards_objetos.pdf`. |
| Cartões não entram automaticamente nos envelopes | IMPLEMENTADO | `generator/package_builder.py` chama `build_printable_card_documents()` depois do merge de envelopes e adiciona arquivos com categoria `printable_support`; `print_guide.py` instrui imprimir separado dos envelopes. | Confirmado no manifest fake: `player_files` só contém envelopes; printables aparecem como apoio de mesa. |
| Mapas P2 | PARCIALMENTE IMPLEMENTADO | `generator/floorplan_renderer.py` abre gaps de portas, desenha janelas/câmeras em paredes e gera SVG P&B; `generator/visual_procedural.py` renderiza `floorplan.html` com `landscape=True`; validator tem códigos `MAP_*`. | Implementação existe; revisão geométrica/visual final depende de baseline real. |
| Landscape obrigatório de mapa | PARCIALMENTE IMPLEMENTADO | `MapaProcedural.orientacao` default é `landscape`; `build_visual_documents()` força `landscape=True`; validator bloqueia orientação diferente de landscape. | Comprovado por código; orientação real do PDF não foi validada com Chromium. |
| Ausência de rotas/solução em mapas | IMPLEMENTADO | Validator procura termos proibidos em título, categoria, áreas, conexões, marcadores, legenda e portas com `MAP_008` e `MAP_010`. | Guardrail textual implementado; não substitui inspeção visual humana. |
| Hotel Aurora sem mapa | IMPLEMENTADO | `examples/caso_canonico_intermediario.json` tem `visual_procedural.mapas: []`; teste `test_hotel_aurora_continua_sem_mapa` existe; documentação de floorplans afirma que Aurora permanece sem mapa. | Alinhado à documentação vigente. |
| Assinaturas/rubricas/manuscritos P3 | IMPLEMENTADO | `generator/signature_renderer.py` gera SVG inline para assinatura/rubrica e manuscrito curto; `models.py` possui perfil de assinatura com overrides; validator valida `SIG_*` e `HAND_*`. | Assinatura e rubrica são modos diferentes; rubrica recebe gesto final próprio. |
| Overrides SVG | IMPLEMENTADO | `PerfilAssinatura` aceita `override_assinatura_svg`, `override_rubrica_svg` e aliases; validator exige SVG local válido; assets em `assets/signatures/*/*.svg` existem. | Suporte implementado e documentado. |
| Estrutura editorial | IMPLEMENTADO | `Blueprint` exige `conflito_central`, `objetivos_por_envelope` e `guia_operacional`; também suporta `contratos_evidencia`, `dicas_contextuais` e `visual_procedural`; validator valida progressão, contratos e dicas. | `contratos_evidencia`, `dicas_contextuais` e `visual_procedural` são default/nullable, mas canônicos atuais usam os campos. |
| Guardrails anti-obviedade | PARCIALMENTE IMPLEMENTADO | `generator/obviousness_checker.py` detecta linguagem conclusiva, autoral, confissão, vazamento interno, antecipação de E1 e documento único solucionador; validator integra achados. | É heurístico; distribuição de evidências também aparece em contratos/grafo, mas não há prova de regra matemática completa para “nenhum documento soluciona sozinho” além das heurísticas. |
| Canônico Iniciante — Mirante | PARCIALMENTE IMPLEMENTADO | Arquivo existe, carrega e strict passa; build fake gera PDFs, manifest e print manifest; build real falhou por Chromium ausente. | Implementação lógica ok; baseline visual real pendente. |
| Canônico Intermediário — Aurora | PARCIALMENTE IMPLEMENTADO | Arquivo existe, carrega e strict passa; build fake gera PDFs, manifest e print manifest; build real não pôde ser comprovado pelo ambiente sem Chromium. | Aurora não tem mapa por decisão documentada. |
| Documentação geral | PARCIALMENTE IMPLEMENTADO | Docs cobrem estado atual, roadmap, diretrizes, diegese, anti-obviedade, authoring, pipeline, visual system, printables, signatures e floorplans. | Há uma divergência crítica entre `AGENTS.md` e docs sobre o canônico Intermediário. |
| Baseline visual real | PENDÊNCIA OPERACIONAL | `docs/ROADMAP.md` define baseline real pós-P0/P1/P2/P3 como próximo passo; build real falhou por Chromium ausente; não há screenshots de validação no repositório. | Não é defeito de implementação; é pendência operacional. |
| Testes de layout/screenshot | NÃO IMPLEMENTADO | Busca por imagens/screenshot encontrou apenas PDFs em `output/sinal_verde_demo` e `output/teste_boletim.pdf`; não há screenshots de validação visual versionados. | Testes unitários cobrem renderer/landscape, mas não inspeção visual documentada dos PDFs canônicos. |
| Estado dos playtests | IMPLEMENTADO | `docs/playtests/INTERMEDIARIO_RODADA_01.md` e refinamento diegético existem; `docs/ESTADO_ATUAL.md` e `docs/ROADMAP.md` incorporam aprendizados do Aurora. | Há registro com participantes, tempo e problemas/ajustes. |
| Canônicos na documentação operacional | IMPLEMENTADO MAS DIFERENTE DO DOCUMENTADO | `AGENTS.md` diz que só Mirante é canônico atual e para não referenciar `caso_canonico_intermediario.json`; `docs/ESTADO_ATUAL.md` afirma duas réguas canônicas, incluindo Aurora validado. | Divergência documental real e relevante para agentes. |

---

## 3. Auditoria por Bloco

### BLOCO 1 — Pipeline Principal

**Status: IMPLEMENTADO com pendência operacional de Chromium para build real.**

Evidências:

- Modelos do blueprint em `generator/models.py`, incluindo `Blueprint`, `Documento`, `ContratoEvidencia`, `VisualProcedural` e `PrintableCard`.
- Schemas YAML em `generator/schemas/*.yaml`.
- Validator em `generator/validator.py`, com método `validar()` chamando todas as etapas principais.
- Renderer em `generator/renderer.py`, com `_html_para_pdf()` usando Playwright/Chromium.
- Package builder em `generator/package_builder.py`, com `build_package()` encadeando validação → renderização → visual procedural → merge → manifests → relatórios.
- Merge em `generator/merger.py`, com `pikepdf` oficial e fallback `pypdf`.
- CLI em `scripts/build_package.py`.
- Build fake dos dois canônicos gerou envelopes, dicas, guia do facilitador, guia de impressão, `manifest.json`, `print_manifest.json`, `qa_report.json`, `graph_report.json`, `llm_feedback.json` e `playtest_report.json`.

Divergência/risco:

- Build real depende de Chromium. No ambiente auditado, o executável não existia e a instalação falhou por HTTP 403.

Classificação dos itens:

| Item | Status |
|---|---|
| Blueprint JSON | IMPLEMENTADO |
| Schemas YAML | IMPLEMENTADO |
| Validator | IMPLEMENTADO |
| Package builder | IMPLEMENTADO |
| Renderização HTML | IMPLEMENTADO |
| Renderização PDF | PARCIALMENTE IMPLEMENTADO |
| Integração Playwright | PARCIALMENTE IMPLEMENTADO |
| Merge PDF | IMPLEMENTADO |
| Manifest | IMPLEMENTADO |
| Print manifest | IMPLEMENTADO |

---

### BLOCO 2 — Sistema Visual P0

**Status: IMPLEMENTADO.**

Evidências:

- `templates/styles/document_system.css` contém tokens globais, fontes locais/sistema, escala de espaçamento, linhas, cores P&B, carimbos, famílias documentais, tabelas e media print.
- `generator/renderer.py` injeta esse CSS via `_document_system_css()` e `_injetar_css_documental()`.
- `generator/renderer.py` injeta classes `doc-system`, `doc-type-*`, `doc-family-*`, `doc-player` e `facilitator-doc`.
- Cabeçalho e rodapé documentais são gerados por `_documento_stamped_header_footer()` e `_documento_footer()` para templates de jogador.
- CSS diferencia facilitador com fundo/carcaça visual e carimbo textual `CONFIDENCIAL — FACILITADOR`.

Observações:

- A implementação é real e aplicada pelo renderer, não apenas documentada.
- A qualidade visual final ainda precisa de baseline real em PDF com Chromium, mas isso não invalida a existência do sistema P0.

---

### BLOCO 3 — Printables P1

**Status: IMPLEMENTADO.**

Evidências:

- `TipoPrintableCard` inclui `personagem`, `local` e `objeto`.
- `PrintableCard` existe em `generator/models.py`.
- `generator/printable_cards.py` gera PDFs em `printables/` por tipo e `cards_todos.pdf`.
- `templates/printable_cards.html` existe.
- `generator/package_builder.py` adiciona cartões ao manifest como `printable_support`, fora dos envelopes.
- `generator/print_guide.py` instrui: “Imprimir separado dos envelopes; recortar cartões quando indicado. Não tratar como documento de prova nem substituir evidências.”
- Build fake do Mirante gerou:
  - `printables/cards_personagens.pdf`
  - `printables/cards_locais.pdf`
  - `printables/cards_objetos.pdf`
  - `printables/cards_todos.pdf`
- Build fake do Aurora gerou:
  - `printables/cards_personagens.pdf`
  - `printables/cards_locais.pdf`
  - `printables/cards_todos.pdf`

Observações:

- Aurora não gerou `cards_objetos.pdf` porque o blueprint não contém cartão do tipo `objeto`; isso é comportamento esperado, não falha.
- Os cartões não entram automaticamente nos envelopes; aparecem em `visual_support_files`/`printable_support`.

---

### BLOCO 4 — Mapas P2

**Status: PARCIALMENTE IMPLEMENTADO.**

Evidências implementadas:

- `generator/floorplan_renderer.py` gera SVG P&B com paredes, portas, janelas e câmeras.
- Portas abrem gaps por parede em `_gap_segments()` e espelham gap em área adjacente quando há coincidência real com `_mirrored_door_gap()`.
- Janelas são desenhadas sobre parede via `_window_symbol()`.
- Câmeras são posicionadas em parede via `_camera_symbol()`.
- `generator/visual_procedural.py` renderiza mapas com `landscape=True` usando `templates/floorplan.html`.
- `generator/validator.py` valida orientação `landscape`, áreas inexistentes, portas/janelas/câmeras fora da parede e termos proibidos (`MAP_001` a `MAP_010`).
- `examples/caso_canonico_intermediario.json` declara `visual_procedural.mapas: []`.

Ausência confirmada:

- Não há mapa para “O Último Brinde do Hotel Aurora”. Isso está de acordo com a documentação.

Risco/observação:

- A geometria é validada por regras e testes, mas a auditoria não comprovou renderização visual real com Chromium. Portanto, a classificação é parcial quanto à qualidade final de mapa em PDF.

---

### BLOCO 5 — Assinaturas P3

**Status: IMPLEMENTADO.**

Evidências:

- `generator/signature_renderer.py` implementa `build_signature_svg(personagem, modo="assinatura")`, `build_signature_svg(..., modo="rubrica")` e `build_handwritten_note_svg()`.
- SVG é inline, gerado localmente e sem dependência externa.
- `build_signature_svg()` diferencia modo assinatura e rubrica por dimensões, paths e gesto final próprio para rubrica.
- `PerfilAssinatura` em `generator/models.py` aceita perfil editorial e overrides SVG.
- Validator valida overrides e geração (`SIG_*`, `HAND_*`).
- Assets SVG locais existem em `assets/signatures/*/*.svg`.

Observações:

- O suporte a SVG customizado existe.
- Assinatura, rubrica e manuscrito são elementos diferentes na implementação.

---

### BLOCO 6 — Estrutura Editorial

**Status: IMPLEMENTADO.**

Evidências:

- `ConflitoCentral`, `ObjetivoEnvelope`, `GuiaOperacional`, `ContratoEvidencia`, `DicaContextual` e `VisualProcedural` existem em `generator/models.py`.
- `Blueprint` exige `conflito_central`, `objetivos_por_envelope` e `guia_operacional`.
- Validator consome progressão em `_verificar_progressao_operacional()`.
- Validator consome contratos em `_verificar_contratos_evidencia()`.
- Renderer consome `dicas_contextuais` em `_dicas_contextuais_por_envelope()` e prioriza essas dicas sobre legado.
- Package builder consome `visual_procedural` em `build_visual_documents()`.

Observações:

- `contratos_evidencia` e `dicas_contextuais` possuem default vazio, portanto não são obrigatórios no modelo para blueprints legados. Porém, os canônicos atuais os utilizam e o strict valida coerência.

---

### BLOCO 7 — Guardrails de Anti-Obviedade

**Status: PARCIALMENTE IMPLEMENTADO.**

Evidências:

- `generator/obviousness_checker.py` implementa regras heurísticas para:
  - linguagem conclusiva;
  - linguagem autoral (“compare”, “cruze”, “gabarito” etc.);
  - confissões em primeira pessoa;
  - vazamento de campos internos;
  - nome do culpado perto de verbo incriminador;
  - objetivo narrativo que nomeia culpado + ação;
  - antecipação de solução em E1;
  - chats confessionais;
  - depoimentos como laudos;
  - documento único solucionador.
- `generator/validator.py` integra o checker em `_verificar_obviedade()`.
- `docs/ANTI_OBVIEDADE.md` documenta as regras.

Classificação por subitem:

| Subitem | Classificação | Motivo |
|---|---|---|
| Documento não concluir sozinho | PARCIALMENTE IMPLEMENTADO | Há heurística `_check_single_document_solution`, mas não prova lógica completa. |
| Hipótese parcial em E1 | IMPLEMENTADO | Validator tem `PROG_018` e checker tem antecipação de E1. |
| Fechamento em E2 | PARCIALMENTE IMPLEMENTADO | Modelos/contratos/guia estruturam progressão; não há garantia automática sem revisão editorial. |
| Distribuição de evidências | PARCIALMENTE IMPLEMENTADO | Contratos e grafo verificam cobertura, mas a distribuição continua dependente de modelagem editorial. |
| Ausência de documento único solucionador | PARCIALMENTE IMPLEMENTADO | Checker heurístico existe; não substitui auditoria humana. |

Observação:

- A documentação chama esses mecanismos de guardrails, e isso condiz com a implementação heurística. Não há evidência de prova formal de solvabilidade ou de não-obviedade.

---

### BLOCO 8 — Casos Canônicos

#### 8.1 `examples/caso_canonico_iniciante.json` — “O Desvio da Reserva Mirante”

**Status: PARCIALMENTE IMPLEMENTADO.**

Evidências:

- Arquivo existe e possui título/dificuldade corretos.
- Validator strict passou com risco baixo, 0 críticos e 0 moderados.
- Build fake passou e gerou PDFs sintéticos, manifest, print manifest e relatórios.
- Build fake registrou mapa procedural no manifest como `VP-MAPA-casa_acervo_mirante_andar_1`, final file `01_envelope_1.pdf`, orientation `landscape` e map category `documento_jogador`.

Limitação:

- Build real com Chromium falhou por ausência do executável Chromium local.

#### 8.2 `examples/caso_canonico_intermediario.json` — “O Último Brinde do Hotel Aurora”

**Status: PARCIALMENTE IMPLEMENTADO.**

Evidências:

- Arquivo existe e possui título/dificuldade corretos.
- Validator strict passou com risco baixo, 0 críticos e 0 moderados.
- Build fake passou e gerou PDFs sintéticos, manifest, print manifest e relatórios.
- `visual_procedural.mapas` é lista vazia, em conformidade com a decisão de playtest/documentação.

Limitação:

- Build real com Chromium não pôde ser comprovado neste ambiente.

---

### BLOCO 9 — Documentação

**Status: PARCIALMENTE IMPLEMENTADO.**

| Documento | Status | Evidência/observação |
|---|---|---|
| `docs/ESTADO_ATUAL.md` | PARCIALMENTE CORRETO | Descreve stack e recursos implementados; também reconhece baseline real como próximo passo. Diverge do `AGENTS.md` quanto ao Intermediário. |
| `docs/ROADMAP.md` | CORRETO | Marca P0/P1/P2/P3 como concluídos e baseline real como próximo passo; isso corresponde à auditoria. |
| `docs/LLM_OPERATING_MANUAL.md` | CORRETO | Orienta diagnóstico e preserva prioridades; inclui os dois canônicos como réguas atuais. |
| `docs/DIRETRIZES_EDITORIAIS.md` | CORRETO | Regras editoriais são compatíveis com guardrails e modelos. |
| `docs/DIEGESE_DOCUMENTAL.md` | CORRETO | Diretrizes diegéticas existem e são compatíveis com anti-obviedade/contratos, embora revisão editorial permaneça humana. |
| `docs/ANTI_OBVIEDADE.md` | CORRETO COM LIMITAÇÃO | Descreve regras; implementação existe como heurística. |
| `docs/BLUEPRINT_AUTHORING_GUIDE.md` | CORRETO | Compatível com campos estruturados em `models.py`. |
| `docs/CASE_DESIGN_PIPELINE.md` | CORRETO | Compatível com progressão/contratos/diegese documentada. |
| `docs/VISUAL_SYSTEM.md` | CORRETO COM PENDÊNCIA | P0/P1/P2/P3 existem; baseline visual real segue pendente. |
| `docs/PRINTABLES.md` | CORRETO | Implementação P1 confirma cartões apartados e manifest/print manifest. |
| `docs/SIGNATURES_AND_HANDWRITING.md` | CORRETO | Implementação P3 confirma SVG procedural, rubrica distinta e overrides. |
| `docs/FLOORPLANS.md` | CORRETO COM PENDÊNCIA | Implementação P2 existe, mas revisão visual real ainda pendente. |
| `AGENTS.md` | DESATUALIZADO/DIVERGENTE | Diz para não referenciar `caso_canonico_intermediario.json` salvo pedido explícito, enquanto documentação oficial atual trata Aurora como canônico Intermediário validado. |

Implementação sem documentação relevante:

- Não foi encontrada implementação significativa sem documentação correspondente entre os blocos auditados. O principal problema é divergência documental, não ausência de documentação.

Documentação sem implementação:

- Screenshots/inspeção visual documentada de baseline real aparecem como necessidade/checklist, mas não há evidência implementada/versionada. Classificação: **pendência operacional**.

---

### BLOCO 10 — Baseline Visual

**Status: PENDÊNCIA OPERACIONAL.**

Evidências existentes:

- Renderização real via Playwright está implementada no código.
- Há PDFs em `output/sinal_verde_demo` e `output/teste_boletim.pdf`, modificados em 2026-06-06, mas não são os pacotes canônicos Mirante/Aurora.
- Não foram encontradas screenshots de validação visual versionadas.
- Não há documento de inspeção visual final pós-P0/P1/P2/P3 para os dois canônicos.
- `docs/ROADMAP.md` explicitamente define baseline real pós-P0/P1/P2/P3 como próximo passo.

Comprovação operacional:

- Build real falhou por Chromium ausente.
- Instalação de Chromium falhou por HTTP 403.

Classificação:

- Não é defeito de implementação do pipeline.
- É pendência operacional para revisão visual real.

---

### BLOCO 11 — Estado dos Playtests

**Status: IMPLEMENTADO.**

Evidências:

- `docs/playtests/INTERMEDIARIO_RODADA_01.md` registra o playtest do Hotel Aurora com participantes, tempo total de 100 minutos, problemas e recomendações.
- `docs/playtests/INTERMEDIARIO_RODADA_01_REFINAMENTO_DIEGETICO.md` registra refinamentos documentais/diegéticos.
- `docs/ESTADO_ATUAL.md` incorpora aprendizados: progressão em 2 envelopes, objetivo mais claro, dicas mais úteis, manutenção sem mapa.
- `docs/ROADMAP.md` define novo playtest do Intermediário como fase futura após baseline real.

Observação:

- Há registro de playtest intermediário e seus aprendizados aparecem na documentação/roadmap/diretrizes operacionais.

---

### BLOCO 12 — Divergências Críticas

Ver seção 4 abaixo.

---

## 4. Divergências Encontradas

### 1. `AGENTS.md` diverge da documentação atual sobre o canônico Intermediário

- **Status:** IMPLEMENTADO MAS DIFERENTE DO DOCUMENTADO.
- **Severidade:** alta.
- **Evidência:**
  - `AGENTS.md` diz que o caso canônico atual é apenas “O Desvio da Reserva Mirante” e orienta não recriar nem referenciar `caso_canonico_intermediario.json` salvo pedido explícito.
  - `docs/ESTADO_ATUAL.md` afirma que o projeto mantém duas réguas canônicas validadas, incluindo “O Último Brinde do Hotel Aurora” em `examples/caso_canonico_intermediario.json`.
  - O arquivo `examples/caso_canonico_intermediario.json` existe, valida em strict e builda com fake PDF.
- **Impacto:** agentes podem evitar auditar/manter o Aurora ou tratar o arquivo como indevido, apesar da documentação oficial atual e do pedido desta auditoria exigirem sua validação.
- **Risco:** decisões automatizadas inconsistentes sobre o que é canônico.

### 2. Baseline visual real pós-P0/P1/P2/P3 ainda não existe no repositório

- **Status:** PENDÊNCIA OPERACIONAL.
- **Severidade:** média.
- **Evidência:**
  - `docs/ROADMAP.md` define baseline real como próximo passo.
  - Build real falhou por Chromium ausente.
  - `python -m playwright install chromium` falhou com HTTP 403.
  - Não há screenshots ou relatório de inspeção visual versionado dos canônicos.
- **Impacto:** não há prova de que PDFs reais via Chromium estejam visualmente bons após P0/P1/P2/P3.
- **Risco:** quebras de layout, overflow, assinaturas mal posicionadas ou mapa/cartões com problemas só aparecerão no baseline real.

### 3. Documentação “tecnicamente funcional” pode ser lida como build real comprovado, mas a evidência atual só comprova build fake neste ambiente

- **Status:** PARCIALMENTE IMPLEMENTADO.
- **Severidade:** média.
- **Evidência:**
  - Código de Playwright existe.
  - Validator strict passa.
  - Build fake passa.
  - Build real falha no ambiente auditado por Chromium ausente.
- **Impacto:** o pipeline existe, mas a auditoria não comprovou geração real de PDFs canônicos com Chromium.
- **Risco:** falso senso de conclusão se build fake for confundido com baseline visual real.

### 4. Anti-obviedade é documentado como guardrail, mas permanece heurístico

- **Status:** PARCIALMENTE IMPLEMENTADO.
- **Severidade:** baixa.
- **Evidência:** `generator/obviousness_checker.py` usa padrões e heurísticas textuais; a própria doc descreve o checker como guardrail, não prova formal.
- **Impacto:** pode não detectar todos os documentos que resolvem demais, ou pode depender de revisão humana para contexto.
- **Risco:** vazamento editorial sutil que não use os termos/padrões bloqueados.

---

## 5. Riscos Reais

Somente riscos comprovados por evidência local:

1. **Risco de agentes seguirem instrução desatualizada sobre canônicos.**
   - Evidência: divergência entre `AGENTS.md` e `docs/ESTADO_ATUAL.md` sobre `caso_canonico_intermediario.json`.

2. **Risco de layout real não validado nos canônicos.**
   - Evidência: baseline visual real está no roadmap como próximo passo; build real falhou por Chromium ausente; não há screenshots/relatório visual versionado.

3. **Risco de confundir build fake com build real.**
   - Evidência: builds fake passaram com `INDICIARIO_ALLOW_FAKE_PDF=1`; build real falhou no ambiente.

4. **Risco residual de anti-obviedade não cobrir vazamentos sutis.**
   - Evidência: checker é heurístico e baseado em padrões textuais.

---

## 6. Próximo Passo Recomendado

Limitado aos três itens permitidos pelo escopo:

1. **Baseline visual real dos canônicos.**
   - Instalar/fornecer Chromium em ambiente local capaz de executar Playwright.
   - Rodar:
     ```bash
     python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
     python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
     ```
   - Registrar evidências: PDFs finais, manifests, print manifests e screenshots/relatório de revisão visual.

2. **Correções comprovadas de renderização/layout.**
   - Corrigir somente falhas observadas no baseline real: overflow, páginas quebradas, assinatura/rubrica mal posicionada, cartão cortando texto, mapa com problema visual, guia de impressão ambíguo ou separação incorreta de arquivos.

3. **Novo playtest do Intermediário.**
   - Executar após baseline real e eventuais correções comprovadas.
   - Registrar tempo, travamentos, necessidade de dicas, clareza do E1/E2, uso de cartões e percepção de diversão/justiça.

Não há evidência objetiva nesta auditoria que justifique marketplace, dashboard, editor visual, banco de dados, Telegram, multiusuário, IA de imagem ou Canônico Avançado agora.
