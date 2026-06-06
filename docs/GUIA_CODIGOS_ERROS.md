# Guia de códigos de erro e aviso editorial

Este guia documenta os códigos `OBV_xxx`, `PT_xxx` e `GP_xxx` existentes no código atual. Ele não inventa novos códigos nem severidades. Se um relatório mencionar código não listado aqui, **verificar no código antes de agir**.

Fontes usadas: `docs/ANTI_OBVIEDADE.md`, `generator/obviousness_checker.py`, `generator/playtest_metrics.py`, `generator/clue_graph.py` e testes relacionados.

## Como ler severidade e bloqueio

- `OBV_xxx` vem do guardrail anti-obviedade. No checker, severidades são `critical`, `moderate` e `warning`; no validator, elas viram respectivamente `CRÍTICO`, `MODERADO` e `AVISO`.
- No validator, qualquer crítico bloqueia geração. Quatro ou mais moderados bloqueiam; dois ou três moderados bloqueiam em modo `--strict`; um moderado não bloqueia sozinho.
- `PT_xxx` é relatório heurístico de playtest/carga. No código atual, os achados são `warning` e não aparecem como erro bloqueante direto do relatório de playtest.
- `GP_xxx` é relatório de grafo de pistas. O relatório retorna `failed` se houver issue `critical`; retorna `passed` se não houver críticos. Quando não há contratos, retorna `skipped` com `GP_006` como warning.

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
| PT_001 | warning | Não bloqueia diretamente no relatório PT | Documentos acima do recomendado para a dificuldade declarada | Carga de leitura pode exceder a promessa do nível | Reduzir documentos, dividir caso, aumentar dificuldade declarada ou justificar em playtest |
| PT_002 | warning | Não bloqueia diretamente no relatório PT | Documentos abaixo do recomendado para a dificuldade declarada | Caso pode ficar raso, curto ou com pouca investigação | Adicionar evidência real, falso caminho justo ou recontextualização, sem encher por volume |
| PT_003 | warning | Não bloqueia diretamente no relatório PT | Suspeitos acima do recomendado para a dificuldade declarada | Grupo pode dispersar hipóteses e perder foco | Fundir personagens, reduzir suspeita aparente ou melhorar descarte |
| PT_004 | warning | Não bloqueia diretamente no relatório PT | Envelope desbalanceado | Um envelope concentra documentos demais e alonga uma fase | Redistribuir documentos, dividir progressão ou explicitar critério de avanço |
| PT_005 | warning | Não bloqueia diretamente no relatório PT | Nenhum red herring identificado | Caso pode ficar linear ou óbvio | Adicionar mentira plausível ou suspeito aparente com descarte justo |
| PT_006 | warning | Não bloqueia diretamente no relatório PT | Red herrings excessivos em relação aos contratos obrigatórios | Ruído pode superar investigação e parecer injusto | Reduzir falsos caminhos ou criar contratos de descarte mais claros |
| PT_007 | warning | Não bloqueia diretamente no relatório PT | Contratos obrigatórios excessivos para a dificuldade declarada | Cadeia lógica pode ficar longa demais para o nível | Consolidar contratos, rebaixar obrigatoriedade ou ajustar dificuldade |
| PT_008 | warning | Não bloqueia diretamente no relatório PT | Tempo estimado incompatível com tempo declarado | Promessa de sessão pode frustrar o grupo | Ajustar tempo declarado, carga documental ou estrutura de envelopes |
| PT_009 | warning | Não bloqueia diretamente no relatório PT | Dificuldade declarada diverge muito da dificuldade estimada | Caso pode estar rotulado incorretamente | Reavaliar dificuldade, contagem de documentos, contratos e suspeitos |

## Códigos GP — grafo de pistas

| Código | Severidade no código | Bloqueia geração? | Significado | Impacto editorial | Ação recomendada |
|---|---|---|---|---|---|
| GP_001 | critical | O relatório GP fica `failed` | Contrato de evidência não define `prova_principal` | Passo lógico não tem documento base | Definir prova principal existente ou remover/reescrever contrato |
| GP_002 | critical | O relatório GP fica `failed` | Contrato de evidência não define `conclusao` | Não está claro que conclusão o jogador deve tirar | Escrever conclusão editorial do contrato sem vazar para documento de jogador |
| GP_003 | warning | Não torna GP `failed` sozinho | Documento não participa de nenhum contrato de evidência | Documento pode ser órfão, decoração ou ruído sem função | Conectar documento a contrato, justificar como apoio/ambientação ou remover |
| GP_004 | warning | Não torna GP `failed` sozinho | Contrato não obrigatório e não final pode ser beco sem saída lógico | Cadeia pode ter ramo que não ajuda avanço nem solução | Tornar obrigatório, marcar função final quando for o caso, ou rebaixar/remover contrato |
| GP_006 | warning ou critical | Warning quando nenhum contrato existe; critical quando nenhum contrato final existe | Grafo não avaliado por ausência de contratos, ou ausência de contrato de solução final | Sem contratos não há análise; sem final não há alvo claro de solução | Criar contratos de evidência; garantir contrato final com prova e confirmação independentes |
| GP_007 | critical | O relatório GP fica `failed` | Contrato final não tem caminho documental mínimo válido | Solução final não tem prova principal e confirmação independente válidas | Definir prova principal e confirmação independente distintas, existentes e suficientes |

## Lacunas conhecidas

- `GP_005` não foi encontrado em `generator/clue_graph.py` no estado atual. Se aparecer em relatório futuro, **verificar no código antes de agir**.
- Códigos fora das famílias `OBV_xxx`, `PT_xxx` e `GP_xxx` existem em outros validadores, mas estão fora do escopo deste guia.
