# Guia de códigos de erro e aviso editorial

Este guia documenta os códigos `OBV_xxx`, `PT_xxx`, `GP_xxx`, `ER_xxx` (validator/qualidade editorial) e `RV_xxx`, `PV_xxx`, `FP_xxx`, `LS_xxx`, `CJ_xxx`, `SM_xxx` (pipeline multiagente/Provider) existentes no código atual. Ele não inventa novos códigos nem severidades. Se um relatório mencionar código não listado aqui, **verificar no código antes de agir**.

Fontes usadas: `docs/ANTI_OBVIEDADE.md`, `docs/QUALITY_COMPARATIVE_REPORT.md`, `generator/obviousness_checker.py`, `generator/playtest_metrics.py`, `generator/clue_graph.py`, `generator/evidence_reviewer.py` e testes relacionados.

## Como ler severidade e bloqueio

- `OBV_xxx` vem do guardrail anti-obviedade. No checker, severidades são `critical`, `moderate` e `warning`; no validator, elas viram respectivamente `CRÍTICO`, `MODERADO` e `AVISO`.
- No validator, qualquer crítico bloqueia geração. Quatro ou mais moderados bloqueiam; dois ou três moderados bloqueiam em modo `--strict`; um moderado não bloqueia sozinho.
- `PT_xxx` é relatório heurístico de playtest/carga. No código atual, os achados são `warning` e não aparecem como erro bloqueante direto do relatório de playtest.
- `GP_xxx` é relatório de grafo de pistas. O relatório retorna `failed` se houver issue `critical`; retorna `passed` se não houver críticos. Quando não há contratos, retorna `skipped` com `GP_006` como warning.
- `ER_xxx` vem do `evidence_reviewer` e mede cadeia de evidência, suporte dos pilares, red herrings e vazamento de informação. Findings ER_006, ER_007 e ER_008 compõem métrica de `vazamento_info` em `docs/QUALITY_COMPARATIVE_REPORT.md`; portanto são `lower_is_better`, não metas esperadas.

## Códigos OBV — anti-obviedade

| Código | Severidade no código | Bloqueia geração? | Significado | Impacto editorial | Ação recomendada |
|---|---|---|---|---|---|
| OBV_001 | warning | Não bloqueia sozinho | Log, sistema ou escala em Intermediário+ usa nome em contexto crítico; deveria preferir código operacional | Facilita demais a associação entre pessoa e ação crítica | Trocar nome por credencial/código e fornecer tradução em documento separado, se necessário |
| OBV_002 | moderate | Pode bloquear conforme quantidade/strict | Nome do culpado aparece junto de verbo incriminador e contexto crítico no mesmo trecho | Documento aproxima demais autoria, ação e prova | Separar nome, ação e contexto em documentos ou trechos diferentes; trocar por fato observado |
| OBV_003 | critical | Sim | Confissão em primeira pessoa em documento do jogador | Entrega autoria diretamente | Reescrever como ruído operacional, registro parcial ou fala ambígua |
| OBV_004 | warning | Não bloqueia sozinho | `objetivo_narrativo` nomeia culpado junto de ação potencialmente incriminadora | Campo interno pode contaminar o tom do documento | Reescrever objetivo com função investigativa, sem culpado + ação |
| OBV_005 | moderate | Pode bloquear conforme quantidade/strict | E1 antecipa solução, gabarito, confissão ou culpado revelado | Envelope inicial deixa de produzir hipótese parcial e passa a resolver o caso | Recalibrar E1 para contradição, ausência, suspeita inicial ou pergunta parcial |
| OBV_006 | moderate | Pode bloquear conforme quantidade/strict | Linguagem conclusiva em documento do jogador | Documento soa como laudo/gabarito, não evidência | Trocar conclusão por registro bruto: “consta”, “indica”, “sem anotação”, “registrado” |
| OBV_007 | critical | Sim | Chat explica o crime diretamente ou contém linguagem confessional | Chat vira confissão de vilão | Reescrever como exportação operacional ambígua com origem clara |
| OBV_008 | moderate | Pode bloquear conforme quantidade/strict | Depoimento afirma autoria, intenção ou plano de terceiro como fato estabelecido | Depoimento deixa de ser versão limitada e vira laudo onisciente | Limitar depoimento ao que a pessoa viu, ouviu ou fez; mover interpretação ao guia |
| OBV_009 | moderate | Pode bloquear conforme quantidade/strict | Documento parece responder sozinho quem, como, por quê e benefício | Quebra a cadeia de evidência | Dividir a descoberta entre hipótese, recontextualização, confirmação e descarte |
| OBV_010 | critical | Sim | Campo ou valor interno do blueprint vazou para conteúdo de documento do jogador | Expõe metadado, gabarito ou cadeia causal ao jogador | Remover vazamento de `conteudo`; manter em metadados, guia ou gabarito |
| OBV_011 | warning | Não bloqueia sozinho | Referência instrucional a código de documento dentro de conteúdo diegético | Documento orienta cruzamento como voz do autor | Remover instrução e códigos diegéticos; mover para dica/guia |
| OBV_012 | moderate | Pode bloquear conforme quantidade/strict | Linguagem de autor/facilitador em conteúdo diegético | Documento parece dica ou checklist de solução | Reescrever como documento real do mundo ficcional |

## Códigos PT — métricas heurísticas de playtest

| Código | Severidade no código | Bloqueia geração? | Significado | Impacto editorial | Ação recomendada |
|---|---|---|---|---|---|
| PT_001 | warning | Não bloqueia diretamente no relatório PT | Documentos acima do recomendado para a dificuldade declarada (contagem é sinal informativo; profundidade dedutiva determina dificuldade estimada) | Carga de leitura pode exceder a promessa do nível | Reduzir documentos, dividir caso, aumentar dificuldade declarada ou justificar em playtest |
| PT_002 | warning | Não bloqueia diretamente no relatório PT | Documentos abaixo do recomendado para a dificuldade declarada | Caso pode ficar raso, curto ou com pouca investigação | Adicionar evidência real, falso caminho justo ou recontextualização, sem encher por volume |
| PT_003 | warning | Não bloqueia diretamente no relatório PT | Suspeitos acima do recomendado para a dificuldade declarada (contagem é sinal informativo; profundidade dedutiva determina dificuldade estimada) | Grupo pode dispersar hipóteses e perder foco | Fundir personagens, reduzir suspeita aparente ou melhorar descarte |
| PT_004 | warning | Não bloqueia diretamente no relatório PT | Envelope desbalanceado | Um envelope concentra documentos demais e alonga uma fase | Redistribuir documentos, dividir progressão ou explicitar critério de avanço |
| PT_005 | warning | Não bloqueia diretamente no relatório PT | Nenhum red herring identificado | Caso pode ficar linear ou óbvio | Adicionar mentira plausível ou suspeito aparente com descarte justo |
| PT_006 | warning | Não bloqueia diretamente no relatório PT | Red herrings excessivos em relação aos contratos obrigatórios | Ruído pode superar investigação e parecer injusto | Reduzir falsos caminhos ou criar contratos de descarte mais claros |
| PT_007 | warning | Não bloqueia diretamente no relatório PT | Contratos obrigatórios excessivos para a dificuldade declarada (contagem é sinal informativo; profundidade dedutiva determina dificuldade estimada) | Cadeia lógica pode ficar longa demais para o nível | Consolidar contratos, rebaixar obrigatoriedade ou ajustar dificuldade |
| PT_008 | warning | Não bloqueia diretamente no relatório PT | Tempo estimado incompatível com tempo declarado | Promessa de sessão pode frustrar o grupo | Ajustar tempo declarado, carga documental ou estrutura de envelopes |
| PT_009 | warning | Não bloqueia diretamente no relatório PT | Dificuldade declarada diverge muito da dificuldade estimada por profundidade (`clue_graph` depth), densidade textual e papel do E2 | Caso pode estar rotulado incorretamente | Reavaliar dificuldade, profundidade da cadeia de solução, densidade textual e papel do E2 |


## Códigos ER — cadeia de evidência (evidence_reviewer)

| Código | Severidade no código | Bloqueia geração? | Significado | Por que prejudica | Como evitar |
|---|---|---|---|---|---|
| ER_002 | major | Não bloqueia sozinho no reviewer; deve barrar aprovação editorial de caso novo | Pilar de validação do E1 sem pista de suporte na `matriz_pistas` | O gate E1→E2 pede defesa documental, mas um dos quatro pilares depende de prosa, intuição ou gabarito interno | Garantir que cada um dos 4 pilares do E1 tenha pelo menos 1 pista na `matriz_pistas` apontando o documento que sustenta esse pilar |
| ER_006 | major | Não bloqueia sozinho no reviewer; deve barrar aprovação editorial de caso novo | Red herring tem documento de descarte, mas nenhuma pista na `matriz_pistas` aponta ou contradiz esse documento | O descarte existe apenas na explicação do autor; o grupo não recebe trilha investigável para inocentar o falso suspeito | Para cada red herring, referenciar o documento de descarte por uma pista explícita; a pista deve contradizer, limitar ou contextualizar o documento que inocenta. Descarte só na prosa do red herring não conta |
| ER_007 | major | Não bloqueia sozinho no reviewer; deve barrar aprovação editorial de caso novo | Contrato com `obrigatoria_para_avanco: true` usa `prova_principal` fora do envelope atual | Vaza informação de envelope futuro para um gate anterior ou transforma revelação/solução do E2 em requisito de avanço; é vazamento evitável e deve ser minimizado (`lower_is_better`), não tratado como esperado | Reservar `obrigatoria_para_avanco: true` para contratos cuja `prova_principal` está no envelope atual: em E1→E2, prova em E1. Modelar revelação e solução do E2 como contrato `fase: "E2"`/`tipo: "recontextualizacao"` e contrato `fase: "final"`/`tipo: "solucao_final"`, com `prova_principal` em E2 e `obrigatoria_para_avanco: false` |
| ER_008 | minor | Não bloqueia sozinho no reviewer; sinaliza dispersão documental | Menos de 40% dos documentos contribuem para alguma pista | O dossiê acumula material órfão, aumenta carga de leitura e dilui a cadeia investigativa | Fazer pelo menos 40% dos documentos contribuírem para alguma pista na `matriz_pistas`, contrato, confirmação ou descarte; documentos de ambientação devem ser minoria consciente |

## Códigos GP — grafo de pistas

| Código | Severidade no código | Bloqueia geração? | Significado | Impacto editorial | Ação recomendada |
|---|---|---|---|---|---|
| GP_001 | critical | O relatório GP fica `failed` | Contrato de evidência não define `prova_principal` | Passo lógico não tem documento base | Definir prova principal existente ou remover/reescrever contrato |
| GP_002 | critical | O relatório GP fica `failed` | Contrato de evidência não define `conclusao` | Não está claro que conclusão o jogador deve tirar | Escrever conclusão editorial do contrato sem vazar para documento de jogador |
| GP_003 | warning | Não torna GP `failed` sozinho | Documento não participa de nenhum contrato de evidência | Documento pode ser órfão, decoração ou ruído sem função | Conectar documento a contrato, justificar como apoio/ambientação ou remover |
| GP_004 | warning | Não torna GP `failed` sozinho | Contrato não obrigatório, não final e não descarte (`tipo != "descarte"`) pode ser beco sem saída lógico. Contratos `tipo == "descarte"` são isentos por design (ISSUE-30.9): seu papel é guiar o descarte de red herring, não ser gate de avanço | Cadeia pode ter ramo que não ajuda avanço nem solução | Tornar obrigatório, marcar função final quando for o caso, ou rebaixar/remover contrato (não se aplica a contratos `tipo == "descarte"`) |
| GP_006 | warning ou critical | Warning quando nenhum contrato existe; critical quando nenhum contrato final existe | Grafo não avaliado por ausência de contratos, ou ausência de contrato de solução final | Sem contratos não há análise; sem final não há alvo claro de solução | Criar contratos de evidência; garantir contrato final com prova e confirmação independentes |
| GP_007 | critical | O relatório GP fica `failed` | Contrato final não tem caminho documental mínimo válido | Solução final não tem prova principal e confirmação independente válidas | Definir prova principal e confirmação independente distintas, existentes e suficientes |

## Códigos RV/PV/FP/LS/CJ/SM — pipeline multiagente (Provider)

Famílias nascidas nas ISSUE-17/31/32/33/33.1/33.2. Não fazem parte do `validator` strict dos blueprints — atuam no pipeline cego (blind bundle → solver → judge → meter). Tabela resumida; contrato completo em cada spec/módulo de origem.

| Código | Módulo | Spec de origem | Significado resumido |
|---|---|---|---|
| RV_001 | `generator/blind_solver_report_validator.py` | `.ai/issues/ISSUE-18_SPEC.md` | Falha estrutural delegada ao validador de schema do report |
| RV_002 | `generator/blind_solver_report_validator.py` | `.ai/issues/ISSUE-18_SPEC.md` | Conclusão presente sem `evidence_used` — bloqueia |
| RV_003 | `generator/blind_solver_report_validator.py` | `.ai/issues/ISSUE-18_SPEC.md` | Alta confiança sem evidência — bloqueia |
| RV_004 | `generator/blind_solver_report_validator.py` | `.ai/issues/ISSUE-18_SPEC.md` | Alta confiança com `open_questions` ainda abertas — bloqueia |
| RV_005 | `generator/blind_solver_report_validator.py` | `.ai/issues/ISSUE-18_SPEC.md` | Sem conclusão e sem `open_questions` — bloqueia |
| RV_006 | `generator/blind_solver_report_validator.py` | `.ai/issues/ISSUE-18_SPEC.md` | `reasoning_summary` só placeholder — warning, não bloqueia |
| RV_007 | `generator/blind_solver_report_validator.py` | `.ai/issues/ISSUE-18_SPEC.md` | Evidência presente mas conclusão vazia — warning, não bloqueia |
| RV_008 | `generator/blind_solver_report_validator.py` | `.ai/issues/ISSUE-18_SPEC.md` | Baixa confiança com evidência majoritariamente `high` — bloqueia |
| RV_009 | `generator/blind_solver_harness.py` | `.ai/issues/ISSUE-33.6_SPEC.md` | `evidence_used` cita `artifact_id` fora de `context.accessed_artifacts` do round — warning `citacao_sem_leitura`, nunca bloqueia. Vive no harness (não no `blind_solver_report_validator.py`) porque só o harness tem acesso ao log de acessos do round |
| RV_010 | `generator/blind_solve_run_record.py` | `.ai/issues/ISSUE-33.6_SPEC.md` | Trilha auditável do RV_009: o warning propaga para `harness_warnings` do run record (campo já existente, sem mudança de schema) |
| PV_001 | `generator/llm_provider.py` | `.ai/issues/ISSUE-31_SPEC.md` | `ProviderRequest.prompt` vazio ou só whitespace |
| PV_002 | `generator/llm_provider.py` | `.ai/issues/ISSUE-31_SPEC.md` | `max_tokens` não é maior que zero |
| PV_003 | `generator/llm_provider.py` | `.ai/issues/ISSUE-31_SPEC.md` | `temperature` fora do intervalo `[0.0, 2.0]` |
| PV_004 | `generator/llm_provider.py` | `.ai/issues/ISSUE-31_SPEC.md` | `system`, quando fornecido, vazio ou só whitespace |
| FP_001 | `generator/fake_provider.py` | `.ai/issues/ISSUE-32_SPEC.md` | Request inválido rejeitado antes de consumir roteiro; não registra em `calls` |
| FP_002 | `generator/fake_provider.py` | `.ai/issues/ISSUE-32_SPEC.md` | Roteiro esgotado — `ProviderResponseError("script exhausted")` |
| FP_003 | `generator/fake_provider.py` | `.ai/issues/ISSUE-32_SPEC.md` | Item do roteiro é `ProviderError` — injeta o erro, mas registra em `calls` |
| FP_004 | `generator/fake_provider.py` | `.ai/issues/ISSUE-32_SPEC.md` | `ProviderResponse.request_id` sempre ecoa o `request_id` recebido |
| LS_001 | `generator/llm_blind_solver.py` | `.ai/issues/ISSUE-33_SPEC.md` | Sentinela de vazamento: conteúdo fora de `included_artifacts` não pode aparecer no prompt |
| LS_003 | `generator/llm_blind_solver.py` | `.ai/issues/ISSUE-33_SPEC.md` | Ids sempre sobrescritos a partir do contexto do harness, nunca aceitos do modelo |
| CJ_001 | `generator/conclusion_judge.py` | `.ai/issues/ISSUE-33.1_SPEC.md` | Prompt do judge contém só dados do report + conclusões esperadas, nada mais |
| CJ_002 | `generator/conclusion_judge.py` | `.ai/issues/ISSUE-33.1_SPEC.md` | Reparo de JSON com `max_repair_attempts` |
| CJ_003 | `generator/conclusion_judge.py` | `.ai/issues/ISSUE-33.1_SPEC.md` | Toda conclusão esperada precisa aparecer na resposta do modelo |
| CJ_004 | `generator/conclusion_judge.py` | `.ai/issues/ISSUE-33.1_SPEC.md` | Classificação (`resolvido`/`nao_resolvido`/`vazamento`/`ambiguo`) derivada em Python puro |
| CJ_005 | `generator/conclusion_judge.py` | `.ai/issues/ISSUE-33.1_SPEC.md` | `met=true` com `evidence_cited` vazio é rebaixado para `met=false` + warning |
| SM_001 | `generator/solvability_meter.py` | `.ai/issues/ISSUE-33.2_SPEC.md` | `runs < 1` ou `temperature` fora de `[0, 2]` — `ValueError` antes de qualquer run |
| SM_002 | `generator/solvability_meter.py` | `.ai/issues/ISSUE-33.2_SPEC.md` | Cada run usa o mesmo bundle/prompt; run que falha (erro de provider/harness/judge) conta como incompleta, não derruba a medição inteira |
| SM_003 | `generator/solvability_meter.py` | `.ai/issues/ISSUE-33.2_SPEC.md` | `solve_rate == 1.0` → `facil`; `>= 0.5` → `medio`; `> 0.0` → `dificil`; senão mais severo |
| SM_004 | `generator/solvability_meter.py` | `.ai/issues/ISSUE-33.2_SPEC.md` | Flags derivadas das classificações de run e completude |
| SM_005 | `generator/solvability_meter.py` | `.ai/issues/ISSUE-33.2_SPEC.md` | `difficulty_framework_ref` faz cross-link com `docs/DIFFICULTY_FRAMEWORK.md` |
| HD_001 | `generator/llm_blind_solver.py` | `.ai/issues/ISSUE-33.4_SPEC.md` | Resultado não-dict entra em reparo, esgotado vira `BlindSolverHarnessError`; `warnings` não-lista normalizado para lista com warning |
| HD_002 | `generator/llm_blind_solver.py` | `.ai/issues/ISSUE-33.4_SPEC.md` | Item de `evidence_used` não-dict → reparo/erro contratual; campos extras filtrados por `fields(BlindSolverEvidence)` com warning |
| HD_003 | `generator/llm_blind_solver.py` | `.ai/issues/ISSUE-33.4_SPEC.md` | Loop de reparo real até `max_repair_attempts` reenvios antes do erro contratual |
| HD_004 | `generator/llm_blind_solver.py` | `.ai/issues/ISSUE-33.4_SPEC.md` | Ids/metadados substituídos antes de inserir conteúdo de artefatos — literal tipo `{bundle_id}` em artefato não é substituído |
| HD_005 | `generator/conclusion_judge.py` | `.ai/issues/ISSUE-33.4_SPEC.md` | `JudgeVerdict` final revalidado contra `judge_verdict.schema.yaml`; `report_run_id` com fallback conforme (`minLength`) |
| CC_001 | `generator/claude_code_provider.py` | `.ai/issues/ISSUE-33.8_SPEC.md` | Confinamento: cwd temporário descartável por chamada + `--tools ""`; nenhum path de repo/bundle entra no argv |
| CC_002 | `generator/claude_code_provider.py` | `.ai/issues/ISSUE-33.8_SPEC.md` | Runner injetável (`Callable[[list[str], str, Path], CompletedRun]`); default via subprocess contra o binário `claude` real (`shutil.which` resolve `claude.CMD` no Windows); testes sempre injetam runner fake, nenhum invoca o binário real |
| CC_003 | `generator/claude_code_provider.py` | `.ai/issues/ISSUE-33.8_SPEC.md` | Binário ausente (`FileNotFoundError`) ou falha de transporte genérica → `ProviderTransportError` (1 retentativa se `max_transport_retries>0`); `returncode != 0` → `ProviderTransportError` com trecho de stderr; stdout vazio → `ProviderResponseError`, sem retry |
| CC_004 | `generator/claude_code_provider.py` | `.ai/issues/ISSUE-33.8_SPEC.md` | argv base `["claude", "-p", "--model", model_id, "--output-format", "text", "--tools", ""]`; `system`, quando fornecido, vira `--system-prompt <texto>`; prompt sempre via stdin, nunca argv |
| CC_005 | `generator/claude_code_provider.py` | `.ai/issues/ISSUE-33.8_SPEC.md` | `supports_temperature = False` — parâmetro de temperatura não existe no canal headless; `solvability_meter` reflete com `reproducibility.temperature = None` + `temperature_note: "provider-controlled"` |
| CC_006 | `generator/solvability_cli.py` | `.ai/issues/ISSUE-33.8_SPEC.md` | CLI (`--bundle`, `--expected`, `--runs`, `--temperature`, `--solver-model`, `--judge-model`, `--out`) executa `measure_solvability` e grava o `SolvabilityReport`; `--temperature` é no-op com warning (provider ignora); resumo humano no stdout |
| CC_007 | `generator/solvability_cli.py` | `.ai/issues/ISSUE-33.8_SPEC.md` | `--out` nunca aponta para dentro do bundle; bundle de entrada nunca é escrito (imutabilidade comprovada por hash) |
| CC_008 | `generator/solvability_cli.py` | `.ai/issues/ISSUE-33.8_SPEC.md` | `--expected` nunca pode ser um blueprint completo (gabarito); guard por assinatura de campos característicos (2+ de `titulo, documentos, personagens, verdade_real, contratos_evidencia, matriz_pistas`) aborta com mensagem orientando extrair só os statements |

## Lacunas conhecidas

- `GP_005` não foi encontrado em `generator/clue_graph.py` no estado atual. Se aparecer em relatório futuro, **verificar no código antes de agir**.
- `LS_002`, `LS_004` e `LS_005` são citados em docstrings/specs como parte do contrato de isolamento, mas não aparecem como código de finding rastreável em `generator/llm_blind_solver.py` no estado atual — comportamento coberto por teste-sentinela (`tests/test_llm_blind_solver.py`), não por código de erro emitido. Verificar no código antes de agir.
- Códigos fora das famílias `OBV_xxx`, `PT_xxx`, `GP_xxx`, `ER_xxx`, `RV_xxx`, `PV_xxx`, `FP_xxx`, `LS_xxx`, `CJ_xxx` e `SM_xxx` podem existir em outros validadores; verificar no código antes de agir.
