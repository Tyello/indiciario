# Roadmap do Indiciário

Este roadmap registra a direção atual do projeto depois dos playtests reais, dos hardenings editorial/técnico/visual até P3 e da entrega inicial do fluxo operacional Indiciário 2.0.

## Estado atual

O Indiciário já possui:

- régua canônica Iniciante: `examples/caso_canonico_iniciante.json` — **O Desvio da Reserva Mirante**;
- régua canônica Intermediária: `examples/caso_canonico_intermediario.json` — **O Último Brinde do Hotel Aurora**;
- validator strict com guardrails editoriais, anti-obviedade, progressão, cartões, assinaturas/manuscrito e mapas;
- package builder com manifest, print manifest, guia de impressão, guia do facilitador, dicas, QA e grafo de pistas;
- sistema visual P0;
- printables apartados P1;
- plantas baixas P2, incluindo `floor_plan.py` como arquitetura estruturada v2 para o Mirante;
- assinaturas/rubricas/manuscritos P3;
- Case Kernel como camada de extração do DNA investigativo;
- Case Review Report como revisão editorial automática pré-pacote;
- Visual Library 2.0 mínima com plantas-base estruturadas genéricas.

O projeto está em fase de **validação de baseline real e playtest adicional**, não em fase de plataforma comercial.

## Fase concluída — Fundação técnica e editorial

Status: **concluída**.

Concluído:

- Blueprint JSON funcional.
- Renderização HTML/CSS para PDF.
- Playwright/Chromium como renderizador oficial.
- Merge PDF com `pikepdf`.
- Schemas YAML por template.
- `required_when`.
- Placeholder blocker.
- QA Report.
- Graph Report.
- Contratos de evidência.
- Grafo de pistas.
- LLM feedback.
- Guia do facilitador.
- Dicas contextuais.
- Guia de impressão.
- Package builder.
- Manifest e print manifest.
- Playtest metrics.

Não reabrir esta fase sem evidência concreta.

## Fase concluída — Qualidade editorial e progressão

Status: **concluída como base, com melhorias futuras incrementais**.

Concluído:

- `docs/ANTI_OBVIEDADE.md`.
- `generator/obviousness_checker.py`.
- Integração `OBV_*` ao validator.
- `conflito_central`, `objetivos_por_envelope` e `guia_operacional` como campos do blueprint.
- Validações de progressão `PROG_*`.
- Diretriz de diegese documental em `docs/DIEGESE_DOCUMENTAL.md`.

Objetivo alcançado:

> impedir que a LLM gere documentos bonitos antes de existir uma investigação jogável.

## Fase concluída — Indiciário 2.0 inicial: núcleo e revisão

Status: **concluída como fluxo operacional inicial**.

Entregou:

- `generator/case_kernel.py`;
- `docs/CASE_KERNEL.md`;
- `tests/test_case_kernel.py`;
- `generator/case_review.py`;
- `scripts/case_review.py`;
- `docs/CASE_REVIEW.md`;
- `tests/test_case_review.py`.

Fluxo oficial consolidado:

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

Contrato operacional:

- o Case Kernel organiza o núcleo investigativo derivado do blueprint;
- o Case Review aponta riscos editoriais antes de investir em PDF, mapa, template ou polimento visual;
- findings `CK_*` e `CR_*` são insumo de revisão, não substituem validator strict nem playtest;
- não inventar narrativa para preencher lacunas apontadas pelo relatório;
- corrigir primeiro progressão, motivação e evidência obrigatória, só depois materialização visual e pacote.

## Fase concluída — Sistema visual base P0

Status: **concluída**.

Entregou:

- `templates/styles/document_system.css`;
- tokens CSS globais;
- classes por tipo e família documental;
- cabeçalho/rodapé documental;
- tabelas P&B first;
- carimbos burocráticos;
- separação visual entre jogador e facilitador.

## Fase concluída — Printables apartados P1

Status: **concluída**.

Entregou:

- `PrintableCard` no modelo;
- `generator/printable_cards.py`;
- `templates/printable_cards.html`;
- PDFs em `printables/`;
- manifest/print manifest com `printable_support`;
- validações `CARD_*`;
- `docs/PRINTABLES.md`.

Regra consolidada:

> cartão é apoio de mesa, não evidência primária.

## Fase concluída — Plantas baixas P2

Status: **concluída como base, com revisão visual real ainda necessária**.

Entregou:

- `generator/floorplan_renderer.py` como renderer legado/compatibilidade;
- `generator/floor_plan.py` como arquitetura estruturada v2 para mapas canônicos;
- `build_mirante_planta()` e `render_floor_plan_svg()` para o mapa v2 do Mirante;
- `templates/floorplan.html` como embalagem HTML/PDF landscape;
- campos estruturais de mapa no blueprint legado: portas, janelas, câmeras, categoria e inclusão por envelope;
- validações `MAP_*` no validator;
- validações geométricas específicas da planta v2 via `validar_planta()`;
- documentação `docs/FLOORPLANS.md`.

Contrato visual:

- A4 paisagem;
- P&B first;
- planta como espaço arquitetônico, não diagrama de caixas;
- paredes compartilhadas por adjacência;
- portas com gap real e representação simplificada;
- portas com cartão podem receber indicador discreto de acesso;
- portão externo quando houver pátio/doca/serviço;
- janelas em paredes;
- câmeras em parede/canto;
- sem rota, solução, área crítica, câmera offline, campo de visão ou linguagem interpretativa.

Estado específico:

- O canônico Iniciante **O Desvio da Reserva Mirante** usa a planta estruturada v2.
- O mapa do Mirante inclui pátio operacional, posto de controle externo, portão de acesso e doca/serviço.
- O canônico Intermediário **O Último Brinde do Hotel Aurora** permanece sem mapa por decisão de playtest.

## Fase concluída — Visual Library 2.0 mínima

Status: **concluída como base mínima, sem integração automática aos canônicos**.

Entregou:

- `docs/VISUAL_LIBRARY_2_0.md`;
- `generator/floor_plan_library.py`;
- `build_hotel_planta_base()` para um térreo operacional genérico de hotel;
- `build_escritorio_planta_base()` para um escritório administrativo genérico;
- testes unitários em `tests/test_floor_plan_library.py`.

Contrato visual:

- offline first;
- P&B first;
- SVG/CSS procedural;
- sem imagem externa, QR code, fonte externa ou IA;
- reutilização do modelo `PlantaBaixa` e do renderer de `generator/floor_plan.py`;
- nenhum caso canônico alterado ou integrado automaticamente.

Estado específico:

- O Mirante continua usando sua planta estruturada v2 própria.
- O Hotel Aurora continua sem mapa por decisão validada de playtest.

## Fase concluída — Assinaturas, rubricas e manuscritos P3

Status: **concluída**.

Entregou:

- `generator/signature_renderer.py`;
- perfis visuais por personagem;
- SVG procedural offline;
- assinatura e rubrica distintas;
- manuscrito curto procedural;
- overrides SVG compatíveis com aliases antigos e novos;
- validações `SIG_*` e `HAND_*`;
- `docs/SIGNATURES_AND_HANDWRITING.md`.

Regra consolidada:

> assinatura, rubrica e manuscrito são características editoriais do personagem, não decoração genérica.

## Próxima fase — Baseline real pós-Indiciário 2.0 inicial/P0/P1/P2/P3

Status: **próximo passo recomendado**.

Objetivo:

Gerar os pacotes reais dos dois canônicos com Playwright/Chromium e revisar visualmente página por página, depois de passar pelo fluxo Blueprint → Case Kernel → Case Review → Visual Library/templates → Build Package.

Comandos:

```bash
python -m scripts.build_package examples/caso_canonico_iniciante.json --output output/iniciante --strict
python -m scripts.build_package examples/caso_canonico_intermediario.json --output output/intermediario --strict
```

Revisar:

- capa geral;
- capas de envelope;
- documentos do jogador;
- guia do facilitador;
- dicas contextuais;
- guia de impressão;
- cartões apartados;
- assinaturas/rubricas;
- manuscritos curtos;
- mapa v2 do Iniciante;
- P&B/escala de cinza.

Critério de conclusão:

- os dois pacotes geram sem erro real de Playwright;
- não há resíduos técnicos;
- não há quebra visual grave;
- o mapa do Iniciante parece planta operacional, não pista visual nem diagrama de caixas;
- pátio, portão, posto de controle, doca, portas com cartão, janelas e câmeras ficam legíveis no PDF real;
- Hotel Aurora continua sem mapa;
- material de jogador, facilitador, dicas e printables estão fisicamente separados.

## Próxima fase — Ajustes finos pós-baseline

Status: **pendente, dependente da revisão visual real**.

Só corrigir problemas comprovados, como:

- overflow de tabela;
- assinatura mal posicionada;
- manuscrito ilegível;
- cartão cortando texto;
- ajuste fino de geometria do `build_mirante_planta()` se o PDF real indicar problema;
- mapa com porta/janela/câmera/portão mal posicionado;
- guia de impressão ambíguo;
- separação de arquivos incorreta.

Não usar esta fase para reabrir narrativa dos canônicos sem evidência de playtest.

## Próxima fase — Novo playtest do Intermediário

Status: **pendente**.

Objetivo:

Testar o Hotel Aurora com pessoas novas, usando o pacote pós-Indiciário 2.0 inicial/P0/P1/P2/P3.

Avaliar:

- clareza da pergunta pública;
- quando o grupo entende que pode abrir E2;
- se E2 recontextualiza sem explicar demais;
- uso real dos cartões apartados;
- necessidade real de dicas;
- clareza do guia do facilitador;
- tempo real de jogo;
- participação de jogadores mais jovens;
- sensação de diversão, intriga e justiça.

Critério de conclusão:

- grupo entende o objetivo de E1;
- E2 muda a leitura sem parecer gabarito;
- facilitador consegue conduzir sem improvisar solução;
- dicas destravam sem substituir investigação;
- documentos continuam interessantes.

## Próxima fase — Canônico Avançado

Status: **não iniciar antes do baseline real e novo playtest do Intermediário**.

Objetivo futuro:

Criar `examples/caso_canonico_avancado.json` como terceira régua editorial.

Direção esperada:

- mais ambiguidade;
- mais cruzamento temporal;
- mais falsos caminhos plausíveis;
- solução justa, mas menos direta;
- 2 ou 3 envelopes, conforme a história pedir;
- mecânica investigativa diferente de Mirante e Hotel Aurora;
- sem aumento artificial de dificuldade por excesso de documentos.

Critério para iniciar:

- baseline visual dos dois canônicos revisado;
- novo playtest do Intermediário registrado;
- principais problemas de layout/pacote resolvidos;
- plano Markdown do Avançado aprovado antes de gerar JSON.

## Fase futura — Biblioteca canônica completa

Status: **futuro**.

Depois do Avançado, avaliar:

- `caso_canonico_especialista.json`;
- `caso_canonico_mestre.json`.

Cada canônico deve testar uma mecânica investigativa diferente, não apenas uma dificuldade maior.

## Fase futura — Inteligência editorial

Status: **futuro, após vários casos e playtests**.

## Fase concluída — Governança multiagente (Fase A)

Status: **concluída**.

Entregou:

- `docs/MULTIAGENT_OPERATING_PROTOCOL.md`;
- `docs/BLIND_CONTEXT_PROTOCOL.md`;
- `docs/MULTIAGENT_ARTIFACT_RUN_CONTRACTS.md`;
- `.ai/skills/` com skills operacionais;
- mapa de skills futuras em `docs/AGENT_SKILLS.md`.

## Fase concluída — Learning Loop (Fase B)

Status: **concluída na base inicial**.

Entregou:

- `schemas/playtest_session.schema.yaml`;
- `schemas/playtest_finding.schema.yaml`;
- `schemas/learning_decision.schema.yaml`;
- validador do Learning Ledger;
- CLI manual;
- exemplos retrospectivos reais em `examples/learning/retrospective/`.

## Fase concluída — Context Firewall / Blind Bundles (Fase C)

Status: **concluída na base estrutural**.

Entregou:

- `schemas/blind_bundle_manifest.schema.yaml`;
- `generator/artifact_visibility_policy.py`;
- `generator/blind_bundle_generator.py`;
- `generator/blind_bundle_leak_checker.py`;
- `generator/blind_bundle_sanitizer.py`.

## Fase concluída — Blind Solver base (Fase D parcial)

Status: **concluída — ISSUE-16, ISSUE-17, ISSUE-18**.

Entregou:

- `generator/blind_solver_harness.py` — harness com acesso controlado e contexto isolado;
- `schemas/blind_solver_report.schema.yaml` — contrato estrutural do output do solver;
- `generator/blind_solver_report_validator.py` — validador semântico standalone (RV_001–RV_008);
- `schemas/blind_solve_run_record.schema.yaml` — run record rastreável;
- `generator/blind_solve_run_record.py` — builder e validador do run record;
- suite completa passando (ver `docs/ESTADO_ATUAL.md` para contagem atual).

## Fase concluída — Gate Evaluator (Fase D/E)

Status: **concluída** (junho 2026) — ISSUE-19+20.

Objetivo: avaliar se o caso é justo dado o bundle cego; classificar problemas; gerar gate decision.

Classificações de problema:
- pista insuficiente
- pista ambígua
- solução óbvia demais
- excesso de ruído
- quebra de progressão
- vazamento de solução

Entregou:
- `schemas/gate_evaluation.schema.yaml`
- `generator/gate_evaluator.py`
- testes e fixtures

## Fase concluída — Revisores especializados (Fase F)

Status: **concluída** (junho 2026).

Issues agrupadas por eficiência:

### ISSUE-21+22 — Narrative Reviewer + Evidence Reviewer (uma PR)

Status: **concluída** (junho 2026).

Narrative avalia: imersão, diegese, motivação, tom, personagens, documentos que parecem dica.

Evidence avalia: cadeia de evidências, pistas órfãs, buracos lógicos, suporte para cada conclusão.

Entregou: `generator/narrative_reviewer.py`, `generator/evidence_reviewer.py`.

### ISSUE-23 — Visual Reviewer

Status: **concluída** (junho 2026).

Avalia: renderização, legibilidade, densidade visual, mapas, manuscritos, aparência documental.

**Nota:** desbloqueada por ISSUE-28. Baseline visual ainda recomendada antes de implementação pesada.

### ISSUE-24 — Accessibility Reviewer

Status: **concluída** (junho 2026).

Avalia: leitura mobile/tablet, contraste, fonte, sobrecarga cognitiva, impressão.

**Nota:** desbloqueada por ISSUE-28 (mesma dependência que ISSUE-23).

## Fase concluída — Orquestração de runs (Fase G)

Status: **concluída** (junho 2026).

### ISSUE-25+26 — Multiagent Workspace + Manual Orchestrator (uma PR)

Status: **concluída** (junho 2026).

Workspace: diretório padrão por run, artefatos de entrada/saída, logs, findings, gate decisions.

Manual Orchestrator: orquestrar etapas sem LLM automática, comandos manuais, offline, rastreável.

Entregou: `generator/workspace.py`, `generator/manual_orchestrator.py`.

### ISSUE-27 — Run Manifest / Run Summary

Status: **concluída** (junho 2026).

Consolidar tudo que aconteceu em uma run: bundles, agentes, outputs, findings, decisões, próximos passos.

Entregou: `generator/run_manifest.py`.

## Fase concluída — Aplicação em casos reais (Fase H)

Status: **concluída** — ISSUE-28/29/30 concluídas.

Esta é a fase de maior valor — primeiro feedback real do sistema completo.

### ISSUE-28 — Rodar pipeline no caso Hotel Aurora

Status: **concluída** (junho 2026).

Objetivo: aplicar blind bundle → blind solver → gate evaluator → findings → comparar com playtest real.

Entregável: `generator/pipeline_runner.py`, testes, `docs/AURORA_PIPELINE_RUN.md`.

**Esta issue desbloqueia ISSUE-23 e ISSUE-24.**

### ISSUE-29 — Rodar pipeline no caso Fintech

Status: **concluída** (junho 2026).

Validar caso corporativo de dificuldade médio-alta com documentos mais densos.

Entregável: `docs/FINTECH_PIPELINE_RUN.md`.

### ISSUE-30 — Relatório comparativo de qualidade

Status: **concluída** (junho 2026).

Medir evolução: antes/depois, clareza, dificuldade, vazamentos, visual, pacing.

Entregável: `generator/quality_comparative_reviewer.py`, `docs/QUALITY_COMPARATIVE_REPORT.md`.

**Limitações reais da Fase H** (ver `docs/ESTADO_ATUAL.md`):
- o blind solver padrão no `pipeline_runner.py` é um stub determinístico (`DeterministicPipelineSolver`), não resolve o caso de fato. A partir de ISSUE-33, é possível injetar um solver real via parâmetro `solver` (default mantém backward compatibility com o stub);
- `pipeline_runner.py` não invoca os visual/accessibility reviewers (por isso `visual_score=0/0` nos relatórios gerados por ele);
- `compare_to_playtest` só reconhece o caso Aurora.
- Teste cego humano continua sendo a única prova real de solvabilidade.

## Fase futura — Automação com LLM (Fase I)

Status: **futuro, só depois da base testável offline**.

### ISSUE-31 — Provider Interface ✅ concluída

Interface para chamar LLM sem acoplar a OpenAI/Claude/Ollama.

Entregável: `generator/llm_provider.py` — dataclasses frozen (`ProviderRequest`, `ProviderResponse`), `Protocol` runtime_checkable `LLMProvider`, hierarquia de erro (`ProviderError` → `ProviderTransportError`, `ProviderResponseError`), `validate_provider_request` (PV_001–PV_004). Sem chamada de rede, sem implementação concreta de provider (fica pra ISSUE-32). Testes: `tests/test_llm_provider.py` (15 casos). Spec: `.ai/issues/ISSUE-31_SPEC.md`.

### ISSUE-32 — Fake Provider para testes ✅ concluída

Simular respostas previsíveis; CI determinística.

Entregável: `generator/fake_provider.py` — `FakeProvider` satisfaz `LLMProvider` (Protocol da ISSUE-31, sem herança nominal), consome `ScriptedResponse`/`ProviderError` em ordem, injeta falhas (`FP_003`), rejeita request inválido sem consumir roteiro (`FP_001`), esgota roteiro com `ProviderResponseError` (`FP_002`), ecoa `request_id` (`FP_004`). `calls` expõe tupla imutável dos requests recebidos (inclui os que geraram erro injetado, exclui os rejeitados por `FP_001`). Sem rede, sem mutação de `ScriptedResponse`. Testes: `tests/test_fake_provider.py` (7 casos). Spec: `.ai/issues/ISSUE-32_SPEC.md`.

### ISSUE-33 — LLM Blind Solver Adapter ✅ concluída

Conectar modelo real ao harness, mantendo blind bundle como única entrada.

Entregável: `generator/llm_blind_solver.py` — classe `LLMBlindSolver` que satisfaz
`Protocol BlindSolver`. Template versionado em `generator/prompts/blind_solver_v1.md`.
Integração opt-in em `generator/pipeline_runner.py` (parâmetro `solver`, default `None`
preserva stub). Contrato LS_001–LS_005, regra de isolamento (solver nunca com acesso
ao repo). Testes: `tests/test_llm_blind_solver.py`. Spec: `.ai/issues/ISSUE-33_SPEC.md`.

### ISSUE-33.1 — Conclusion Judge ✅ concluída

Avaliar conclusões esperadas contra o relatório do blind solver usando LLM provider.

Entregável: `generator/conclusion_judge.py` — função `judge_conclusions` que recebe
`BlindSolverReport` + lista de `ExpectedConclusionInput` + `LLMProvider`, retorna
`JudgeVerdict` contendo `Conclusion` (id, met, evidence_cited, rationale) para cada
conclusão esperada. Contrato CJ_001–CJ_005, loop de reparo JSON, classificação
(resolvido/nao_resolvido/vazamento/ambiguo) derivada em Python puro. Alimenta campo `met`
do Gate Evaluator. Schema: `schemas/judge_verdict.schema.yaml`. Testes:
`tests/test_conclusion_judge.py`. Spec: `.ai/issues/ISSUE-33.1_SPEC.md`.

### ISSUE-33.2 — Solvability Meter ✅ concluída

Dificuldade calibrada por múltiplas execuções cegas: rodar N vezes solver→juiz sobre o
mesmo bundle e transformar a taxa de resolução em medidor de dificuldade.

Entregável: `generator/solvability_meter.py` — função `measure_solvability` orquestra
N rounds `LLMBlindSolver` + `judge_conclusions` sobre o mesmo bundle, agrega em
`SolvabilityReport` (`solve_rate`, `classification_counts`, `difficulty_estimate`,
`flags`). Contrato SM_001–SM_005; só orquestra e agrega — não altera solver, juiz,
harness ou gate; não decide aprovação. Schema: `schemas/solvability_report.schema.yaml`.
Testes: `tests/test_solvability_meter.py`. Spec: `.ai/issues/ISSUE-33.2_SPEC.md`.

### ISSUE-33.3 — Ligar o Conclusion Judge ao pipeline_runner ✅ concluída

Fecha RISCO-01, DIV-12 e BUG-08 da auditoria (`docs/AUDITORIA_FABLE_2026-07.md`): antes
desta issue, `pipeline_runner._run_gate` fabricava `decision="approved"` incondicionalmente,
mesmo com um `LLMBlindSolver` real injetado — o `judge_conclusions` (ISSUE-33.1) existia mas
não tinha chamador.

Entregável: com `judge_provider: LLMProvider | None = None` injetado em `run_pipeline`/
`_run_gate`, o gate chama `judge_conclusions` de fato e deriva `met` real por conclusão;
`decision`/`gaps` são derivados em Python puro do veredito + regras GE existentes (nunca
confiados ao modelo). Sem `judge_provider`, o comportamento stub é preservado byte a byte.
Manifest ganha `gate_mode: "stub" | "judged"`. Artefato `judge_verdict` passa a ser anexado
ao workspace do run. Falha do provider nunca vira aprovação silenciosa — propaga como falha
rastreável do stage. Typo `EC-GUia-` corrigido para `EC-GUIA-`. Schemas atualizados:
`schemas/run_manifest.schema.yaml`, `schemas/workspace_run.schema.yaml`. Testes:
`tests/test_pipeline_runner.py`. Spec: `.ai/issues/ISSUE-33.3_SPEC.md`.

### ISSUE-34 — LLM Reviewers Adapter

Conectar narrative/evidence/visual reviewers a modelo real.

## Fase concluída — Sistema visual (40.1–40.6)

Status: **concluída** (julho 2026).

Fecha lacunas de fidelidade visual/institucional identificadas na auditoria de junho/2026, fora da série Provider (33.x).

### ISSUE-40.1 — Vendorizar fontes com `@font-face` local

Entregou: fontes locais servidas via `@font-face` no `generator/renderer.py` e `templates/styles/document_system.css`, eliminando dependência de fonte externa no PDF renderizado. Testes: `tests/test_font_vendoring.py`.

### ISSUE-40.2 — Gate visual: detectar fallback de fonte

Entregou: `generator/font_fidelity.py` (`evaluate_font_fidelity`), integrado ao `generator/canonical_quality_gate.py`; detecta fallback silencioso de fonte no PDF gerado. Testes: `tests/test_gate_font_fidelity.py`.

### ISSUE-40.3 — Regras de camada: Tela vs. Papel + remoção do chrome do jogo

Entregou: regras de camada (Camada 0 = chrome do jogo, demais = documento diegético) em `generator/renderer.py`, `templates/base.html` e `templates/styles/document_system.css`; remoção de chrome de UI residual nos templates de documento. Documentado em `framework/20_SISTEMA_VISUAL.md` e `templates/README.md`. Testes: `tests/test_layer_rules.py`.

### ISSUE-40.4 — Papel-cor como taxonomia + remoção do envelhecimento artificial do boletim

Entregou: papel-cor tratado como taxonomia editorial (não efeito decorativo solto) em `templates/styles/document_system.css`; removido envelhecimento artificial do boletim. Documentado em `templates/README.md`. Testes: `tests/test_paper_color_taxonomy.py`.

### ISSUE-40.5 — Isolar `--accent` da marca Indiciário na Camada 0

Entregou: token `--accent` isolado à Camada 0 (`templates/base.html`), impedindo vazamento da marca do produto para dentro do documento diegético. Testes: `tests/test_brand_isolation.py`.

### ISSUE-40.6 — Microidentidades institucionais

Entregou: tokens de microidentidade por instituição (`--inst-color`, `--inst-font-display`, `--inst-header-shape`) em `templates/styles/institution_identity.css`, aplicados em `generator/renderer.py` e templates `cadastro.html`/`manual.html`. Documentado em `framework/20_SISTEMA_VISUAL.md`. Testes: `tests/test_institution_identity.py`.

---

## Workflow multiagente — otimizações ativas

O pipeline de desenvolvimento usa um workflow orquestrador/executor/revisor em `.ai/workflows/`.

Otimizações implementadas a partir de junho/2026:

**Auto-approve para steps low-risk:** steps do tipo `reading`, `baseline`, `documentation` e `wrap-up` não passam pelo revisor — o orquestrador auto-aprova e avança. Reduz ciclos sem ganho real.

**Reports compactos para low-risk:** executor e revisor usam formato reduzido nesses steps.

**Agrupamento de issues:** issues com estrutura idêntica ou dependência direta são implementadas numa PR (19+20, 21+22, 25+26).

**Caveman mode:** todos os agentes operam com output compacto — sem filler, sem hedging, nomes técnicos preservados.

**Sequência não negociável:** ISSUE-23 e ISSUE-24 (Visual/Accessibility Reviewer) só após ISSUE-28 (Aurora no pipeline real).
