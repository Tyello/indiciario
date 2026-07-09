# Protocolo de cegueira e segurança de contexto

## 1. Propósito

Este protocolo define requisitos conceituais para proteger a cegueira de agentes que simulam jogadores, leitores parciais, moderadores cegos ou revisores sem acesso à verdade completa de um caso do Indiciário.

O objetivo é orientar futuras implementações de Context Firewall, blind bundles, políticas de visibilidade, verificadores de vazamento, sanitização não destrutiva, Blind Solver e Gate Evaluator, sem implementar essas capacidades nesta PR.

Este documento parte das seguintes premissas:

- “finja que não conhece a solução” não é isolamento;
- cegueira depende do contexto efetivamente fornecido ao agente;
- segurança documental não substitui isolamento técnico futuro;
- este protocolo não torna o sistema multiagente obrigatório;
- o pipeline atual permanece preservado.

O protocolo também preserva os princípios do Indiciário: offline-first, sem QR code obrigatório, sem internet obrigatória, sem aplicativo externo obrigatório e foco em dedução, investigação, impressão e experiência de grupo.

## 2. Convenções normativas

Este documento usa as mesmas convenções normativas do protocolo operacional:

- **DEVE**: requisito obrigatório;
- **NÃO DEVE**: prática proibida;
- **PODE**: prática permitida;
- **RECOMENDA-SE**: orientação adaptável ao contexto.

Requisitos deste documento podem ser flexibilizados somente por desvio registrado. Recomendações não são bloqueios automáticos. Nenhuma regra documental garante segurança perfeita sem implementação técnica.

## 3. Definição de cegueira

### Cego

Uma execução é **cega** quando o agente recebe somente informações que um jogador teria naquele estágio da experiência. Isso inclui apenas materiais, instruções, ferramentas e regras públicas disponíveis naquele momento.

### Não cego

Uma execução é **não cega** quando o agente pode acessar solução, Bíblia narrativa, contratos de evidência, expectativas privadas, guia do facilitador, gabarito, classificação de pistas ou qualquer informação de autoria indisponível para jogadores.

### Híbrido

Uma execução é **híbrida** quando o agente recebe contexto privado limitado e explicitamente autorizado para uma função específica. Um revisor com acesso parcial a expectativas privadas, um moderador com contexto adicional ou um Gate Evaluator autorizado podem operar em modo híbrido.

### Contaminado

Uma execução é **contaminada** quando o agente recebeu informação proibida, acessou material fora do escopo autorizado ou já conhecia material que invalida a perspectiva cega.

Uma execução contaminada **NÃO DEVE** ser considerada evidência de solvabilidade. Contaminação não pode ser corrigida apenas pedindo ao agente para ignorar o que viu. Uma execução híbrida **NÃO DEVE** ser rotulada como cega. O modo da rodada **DEVE** ser declarado antes da execução.

## 4. Modelo de ameaça

O protocolo considera vazamento qualquer exposição de informação que um papel não deveria conhecer naquele estágio.

### Vazamento por arquivo

Pode ocorrer quando o agente recebe, lê ou tem acesso a arquivos que contenham:

- solução;
- gabarito;
- guia do facilitador;
- Bíblia narrativa;
- contratos de evidência;
- envelopes futuros;
- material de revisão privada.

### Vazamento por nome

Nomes de arquivo podem revelar estrutura autoral ou solução mesmo quando o conteúdo visível parece permitido. Exemplos conceituais proibidos:

- `culpado_marta.pdf`;
- `red_herring_helena.md`;
- `prova_principal.json`;
- `descarte_caio.txt`;
- `solucao_final.yaml`.

### Vazamento por diretório

Caminhos também podem revelar informação privada. Exemplos conceituais proibidos:

- `private/solution/`;
- `culprit/`;
- `future_envelope/`;
- `answer_key/`.

### Vazamento por metadado

Metadados podem carregar informação não visível ao jogador, incluindo:

- título interno;
- autor;
- comentários;
- tags;
- propriedades do PDF;
- campos ocultos;
- nomes de camadas;
- bookmarks;
- notas;
- texto alternativo;
- histórico de revisão.

### Vazamento por conteúdo invisível

Conteúdo invisível ou não renderizado pode expor informações privadas, incluindo:

- comentários HTML;
- texto branco;
- conteúdo fora da página;
- campos ocultos;
- CSS invisível;
- anexos internos;
- texto não renderizado.

### Vazamento por histórico de conversa

O histórico da sessão pode contaminar uma execução quando há:

- agente executado na mesma conversa em que a solução já apareceu;
- memória anterior;
- mensagens de sistema ou ferramenta contendo material privado;
- continuação de sessão previamente não cega.

### Vazamento por instrução operacional

O próprio prompt, papel, formato de saída ou exemplo pode revelar a resposta. Exemplos:

- prompt contendo nomes privados;
- role descrevendo a resposta correta;
- schema de saída com campos reveladores;
- exemplo preenchido com solução real.

### Vazamento por etapa futura

Informações de progressão posterior contaminam um estágio anterior. Exemplos:

- documentos de envelopes ainda não liberados;
- dicas futuras;
- respostas do facilitador;
- conclusões esperadas de etapas posteriores.

### Vazamento por ferramenta

Ferramentas podem romper o isolamento quando permitem:

- busca irrestrita no repositório;
- acesso a diretórios privados;
- leitura automática de arquivos;
- ferramenta de memória;
- indexação sem filtro;
- busca semântica que retorna solução.

### Vazamento semântico

Vazamento semântico ocorre quando informação permitida isoladamente, combinada com nomes, estrutura, ordem, diretórios, metadados ou exemplos, revela a solução ou a classificação autoral. A detecção semântica perfeita não é garantida e **NÃO DEVE** ser presumida por documentação, hashes, nomes neutros ou prompts.

## 5. Classificação conceitual das informações

As categorias abaixo são conceituais e não constituem schema formal nesta PR.

### PUBLIC_PLAYER

Informação disponível ao jogador naquele estágio. Exemplos:

- instruções públicas;
- documentos já liberados;
- mapas públicos;
- ferramentas permitidas;
- pergunta pública;
- regras de avanço já apresentadas.

### PRIVATE_AUTHOR

Informação privada de autoria. Exemplos:

- verdade real;
- segredo central;
- solução;
- planejamento;
- motivação interna;
- arquitetura privada.

### REVIEW_PRIVATE

Informação produzida em revisão. Exemplos:

- findings;
- hipóteses de falha;
- classificação de pistas;
- riscos editoriais;
- análise de red herrings.

### FACILITATOR

Informação disponível apenas ao facilitador. Exemplos:

- gabarito;
- respostas;
- critérios de ajuda;
- instruções de abertura;
- guia de condução.

### FUTURE_STAGE

Informação pública futuramente, mas ainda proibida no estágio atual. Exemplos:

- envelope seguinte;
- dica ainda não solicitada;
- documento liberado por condição;
- resposta parcial posterior.

### DERIVED_REPORT

Relatório gerado por revisão, solver, gate ou auditoria. Pode conter inferências, achados, resultados de gates, hipóteses e incidentes.

### PLAYTEST_ANONYMIZED

Dados de playtest sem informações pessoais desnecessárias. Podem incluir observações, tempos, uso de dicas, travamentos, hipóteses e percepção de diversão, desde que não exponham dados pessoais irrelevantes.

## 6. Matriz de acesso por papel

| Papel | PUBLIC_PLAYER | PRIVATE_AUTHOR | REVIEW_PRIVATE | FACILITATOR | FUTURE_STAGE |
|---|---|---|---|---|---|
| Autor | Sim | Sim | Quando necessário | Quando autorizado | Sim |
| Revisor não cego | Sim | Sim | Sim | Quando necessário | Sim |
| Blind Solver | Sim, apenas estágio atual | Não | Não | Não | Não |
| Participante de mesa simulada | Sim, apenas estágio atual | Não | Não | Não | Não |
| Moderador cego | Sim, apenas estágio atual | Não | Não | Não | Não |
| Gate Evaluator | Sim | Quando autorizado | Sim | Quando necessário | Conforme gate |
| Operador humano | Conforme necessidade | Sim | Sim | Sim | Sim |

Acesso permitido não significa que toda informação deva ser entregue. Cada papel deve receber apenas o mínimo necessário para cumprir sua função. O princípio aplicado é **need to know**. Gate Evaluator não participa da resolução cega que avalia. Operador humano não transforma acesso amplo em permissão para misturar contextos.

## 7. Princípio do menor contexto necessário

Todo agente **DEVE** receber apenas o mínimo necessário para cumprir seu papel. O contexto **NÃO DEVE** incluir material “por conveniência”, documentos privados não utilizados, arquivos de etapas futuras ou exemplos que revelem classificação autoral.

Antes de uma rodada, o operador deve responder:

- qual pergunta o agente precisa responder?
- quais documentos são necessários?
- quais documentos são proibidos?
- qual estágio está sendo simulado?
- quais ferramentas podem ser usadas?
- quais informações o jogador teria?
- quais informações poderiam contaminar a execução?

O protocolo deve preferir exclusão explícita a confiança em autocontrole do agente.

## 8. Context Firewall conceitual

Context Firewall é a capacidade futura de preparar e proteger contexto conforme papel, estágio e visibilidade. Conceitualmente, ele deve ser capaz de:

- selecionar artefatos autorizados;
- excluir materiais proibidos;
- normalizar nomes;
- remover metadados técnicos não visíveis ao jogador;
- registrar transformações;
- calcular hashes;
- gerar manifest;
- criar contexto isolado;
- impedir acesso a etapas futuras;
- registrar violações;
- permitir auditoria posterior.

Nesta PR, Context Firewall é apenas conceito. Nenhuma implementação existe. Nenhum nível de segurança é garantido. Manifest e contratos formais pertencem a issues posteriores.

Hashes podem ajudar a rastrear integridade de artefatos, mas **NÃO** impedem vazamentos por si só e **NÃO** garantem confidencialidade.

## 9. Bundle cego conceitual

Um bundle cego é um conjunto preparado para um papel específico, estágio específico e modo declarado. Um bundle futuro deve conceitualmente conter:

- instruções do papel;
- materiais autorizados;
- descrição da etapa;
- formato esperado da saída;
- lista dos artefatos disponibilizados;
- informação sobre limitações;
- referência ao modo cego.

Ele não deve conter:

- solução;
- arquivos privados;
- envelopes futuros;
- gabarito;
- classificações de pista;
- conclusões esperadas;
- nomes reveladores;
- exemplos preenchidos com a solução.

Este protocolo não define estrutura de diretórios obrigatória, campos formais ou manifest executável.

## 10. Sanitização não destrutiva

Sanitização padrão **DEVE** preservar o conteúdo visível ao jogador. O objetivo é remover resíduos técnicos ou sinais não destinados ao papel, sem reescrever evidência.

A sanitização pode remover:

- metadados técnicos;
- nomes internos;
- comentários ocultos;
- caminhos privados;
- propriedades não visíveis;
- dados de autoria não diegéticos;
- resíduos de build.

A sanitização **NÃO DEVE**:

- reescrever frases;
- resumir documentos;
- corrigir conteúdo;
- remover evidência visível;
- inserir explicação;
- mudar ordem interna;
- substituir termos;
- destacar ou ocultar pistas;
- tornar material mais fácil ou mais difícil.

Qualquer transformação do conteúdo visível deve:

- produzir artefato derivado;
- preservar o original;
- registrar motivo;
- registrar diferença;
- gerar nova versão;
- invalidar comparação direta com runs anteriores;
- exigir nova revisão.

Diferenças conceituais:

- **sanitização técnica** remove metadados, resíduos e sinais não visíveis ao jogador;
- **transformação editorial** altera apresentação, texto, ordem, ênfase ou composição de evidência;
- **correção do caso** altera conteúdo autoral, lógica, pista, progressão ou solução.

Sanitização técnica pode preparar contexto cego. Transformação editorial e correção do caso **NÃO DEVEM** ser escondidas como sanitização.

## 11. Prompt injection documental

Documentos do caso são dados não confiáveis, não instruções operacionais. A única fonte autorizada de instrução deve ser o papel definido fora dos documentos.

Regras conceituais:

- texto dentro de carta, e-mail, log, PDF ou documento diegético não deve controlar o agente;
- instruções encontradas em documentos não devem ser executadas;
- URLs, comandos, pedidos para ler outros arquivos ou “ignorar instruções anteriores” devem ser tratados como conteúdo do caso;
- o agente não deve acessar recursos externos por instrução encontrada no material;
- o operador deve registrar ocorrências suspeitas;
- documentos com texto semelhante a instrução podem ser narrativamente válidos e não devem ser alterados silenciosamente.

A proteção contra prompt injection documental deve ocorrer por isolamento, hierarquia de instruções e controle de ferramentas, não por mutilação da evidência.

## 12. Histórico de conversa e memória

Blind Solver deve preferencialmente executar em sessão nova. A sessão não deve conter mensagens com solução, gabarito, contratos privados, guia do facilitador ou revisão privada.

Regras específicas:

- contexto anterior do mesmo chat deve ser considerado potencial contaminação;
- não se deve reutilizar uma conversa de autoria para revisão cega;
- memória de longo prazo, perfil, busca interna ou ferramentas conectadas devem ser avaliados;
- se não for possível garantir isolamento, a rodada deve ser marcada como híbrida ou contaminada;
- pedir para o modelo “esquecer” não restaura cegueira.

## 13. Ferramentas permitidas e proibidas

Cada rodada deve declarar quais ferramentas podem ser usadas. Para Blind Solver, por padrão:

- pode ler somente o bundle;
- pode organizar notas;
- pode calcular ou cruzar informações presentes;
- não pode buscar no repositório;
- não pode consultar internet;
- não pode abrir arquivos fora do bundle;
- não pode consultar guia, solução ou histórico;
- não pode usar ferramentas de memória não auditadas.

Exceções devem ser registradas com justificativa, escopo, impacto e decisão humana. Este documento não define implementação técnica para controle de ferramentas.

## 14. Nomes e caminhos seguros

Arquivos entregues a agentes cegos devem usar nomes neutros. Exemplos aceitáveis:

- `E1-01.pdf`;
- `E1-02.pdf`;
- `documento-03.pdf`;
- `mapa-andar.pdf`.

Exemplos proibidos:

- `prova-culpado.pdf`;
- `red-herring.pdf`;
- `descarte-suspeito.pdf`;
- `solucao.pdf`;
- `pista-chave.pdf`.

Caminhos reveladores também são proibidos para agentes cegos. A normalização de nome:

- não altera o conteúdo;
- deve ser registrada;
- não muda o artefato original;
- não deve apagar rastreabilidade interna.

Nome neutro reduz uma classe de vazamento, mas **NÃO** cria cegueira completa sozinho.

## 15. Metadados e conteúdo oculto

Checklist conceitual de inspeção antes de entregar artefatos a agentes cegos:

- propriedades do PDF;
- título;
- assunto;
- autor;
- palavras-chave;
- bookmarks;
- anexos;
- comentários;
- camadas;
- texto invisível;
- texto fora da página;
- campos de formulário;
- notas;
- nomes de arquivos incorporados;
- propriedades de imagens;
- HTML oculto;
- CSS;
- atributos de acessibilidade;
- dados EXIF quando houver imagens.

Conteúdo visível ao jogador não pode ser removido silenciosamente. Metadados diegéticos visíveis podem fazer parte da pista. Metadados técnicos não destinados ao jogador podem ser removidos. Dúvida sobre caráter diegético exige decisão humana.

## 16. Envelopes e progressão temporal

O contexto cego deve respeitar o estágio da experiência. Um agente no E1 não deve receber:

- documentos do E2;
- dicas do E2;
- solução final;
- instruções futuras;
- estado esperado após E2;
- conclusões privadas do autor.

Ao liberar novo envelope, o operador deve:

- preservar output anterior;
- registrar o novo conjunto de materiais;
- não reescrever a hipótese anterior;
- comparar mudanças de interpretação;
- manter rastreabilidade entre estágios.

A progressão por envelopes **DEVE** medir como novas evidências recontextualizam hipóteses, não retroativamente editar uma rodada anterior.

## 17. Auditoria da rodada

Uma rodada cega deve permitir responder:

- qual papel foi executado?
- qual estágio foi simulado?
- quais artefatos foram disponibilizados?
- quais foram excluídos?
- quais nomes foram alterados?
- quais metadados foram removidos?
- houve transformação de conteúdo visível?
- qual histórico estava disponível?
- quais ferramentas podiam ser usadas?
- houve incidente?
- a rodada continua válida?
- quem autorizou o uso do resultado?

Contratos formais de run, artifact, manifest e hash pertencem à ISSUE-03 e fases posteriores.

## 18. Classificação de incidentes

Os nomes abaixo são conceituais e não enums executáveis nesta PR.

### LEAK_CONFIRMED

Informação proibida foi disponibilizada.

Consequência:

- rodada inválida como evidência cega;
- gate deve ser BLOCK quando a integridade foi comprometida;
- nova execução necessária.

### LEAK_SUSPECTED

Há suspeita, mas não confirmação.

Consequência:

- gate deve ser INCONCLUSIVE;
- investigar;
- repetir quando necessário.

### OVER_SANITIZATION

Sanitização removeu ou alterou evidência relevante.

Consequência:

- rodada inválida para comparação;
- restaurar artefato;
- revisar processo.

### UNDER_SANITIZATION

Metadado ou conteúdo privado permaneceu acessível.

Consequência:

- tratar como possível vazamento;
- avaliar impacto;
- repetir se necessário.

### TOOL_ESCAPE

Agente acessou recurso fora do contexto autorizado.

Consequência:

- invalidar ou reclassificar rodada;
- registrar incidente.

### HISTORY_CONTAMINATION

Sessão anterior continha informação privada.

Consequência:

- rodada não pode ser classificada como cega.

## 19. Validade da rodada

### Válida

Uma rodada pode ser considerada válida quando:

- contexto compatível com o papel;
- sem vazamento conhecido;
- sem acesso externo proibido;
- sem transformação destrutiva;
- estágio correto;
- output preservado.

Rodada válida pode seguir para avaliação.

### Inválida

Uma rodada deve ser considerada inválida quando houver:

- solução acessível;
- envelope futuro acessível;
- histórico contaminado;
- ferramenta não autorizada usada;
- evidência alterada;
- metadado revelador relevante;
- papel e contexto incompatíveis.

Rodada inválida deve gerar BLOCK quando compromete integridade.

### Inconclusiva

Uma rodada deve ser considerada inconclusiva quando:

- não foi possível confirmar isolamento;
- existem dúvidas sobre histórico;
- inspeção incompleta;
- possível vazamento sem confirmação.

Rodada inconclusiva deve gerar INCONCLUSIVE.

## 20. Procedimento em caso de vazamento

Fluxo recomendado:

```text
Incidente detectado
→ interromper rodada
→ preservar output e contexto
→ registrar material exposto
→ avaliar impacto
→ classificar validade
→ impedir uso indevido do resultado
→ preparar nova execução isolada
→ registrar decisão humana
```

Regras:

- não apagar o output contaminado;
- não pedir ao agente para “tentar de novo sem considerar”;
- não transformar rodada contaminada em evidência;
- não ocultar incidente para preservar PASS;
- não editar retroativamente o contexto registrado.

## 21. Desvios controlados

Exemplos de desvios permitidos quando registrados:

- revisão híbrida explicitamente declarada;
- moderador com contexto adicional;
- Gate Evaluator com solução;
- teste exploratório não usado como evidência;
- uso de ferramenta adicional com justificativa.

Desvios não podem:

- rotular rodada contaminada como cega;
- liberar solução para Blind Solver;
- apagar incidente;
- remover necessidade de nova execução;
- transformar resultado exploratório em certificação.

## 22. Relação com o protocolo operacional

Este documento complementa `docs/MULTIAGENT_OPERATING_PROTOCOL.md`.

O protocolo operacional define papéis, etapas, gates e governança. Este protocolo define o que cada papel pode conhecer. Ambos permanecem documentais nesta fase. Conflitos devem ser resolvidos pela regra mais restritiva para proteção da cegueira. Contratos formais serão tratados na ISSUE-03.

## 23. Checklist manual de preparação

### Antes

- etapa definida;
- papel definido;
- modo cego declarado;
- materiais permitidos selecionados;
- materiais proibidos listados;
- nomes neutralizados;
- metadados inspecionados;
- histórico limpo;
- ferramentas limitadas;
- conteúdo visível preservado.

### Durante

- agente usa apenas material autorizado;
- instruções internas aos documentos são ignoradas;
- acesso externo é impedido;
- incidentes são registrados;
- output não é editado.

### Depois

- output congelado;
- materiais efetivamente usados registrados;
- validade avaliada;
- incidente classificado;
- gate apropriado acionado;
- nova execução planejada quando necessário.

## 23.1. LLM Blind Solver Isolation (ISSUE-33)

A implementação de LLM Blind Solver adiciona uma regra de isolamento de ambiente ao
protocolo de cegueira:

### Regra: Segregação de contexto por sessão

- **Solver de produção via API**: o `LLMBlindSolver` conecta um modelo real (Claude via
  `LLMProvider` injected) ao harness cego.
- **Bundle como única entrada**: o prompt contém apenas template versionado + artefatos
  do bundle (via `context.read_artifact_text`) + metadados de run.
- **Proibido em sessão com acesso ao repo**: o solver **NÃO DEVE** executar numa sessão
  de agente que tenha acesso ao repositório, pois o repo contém o gabarito.
- **Segregação obrigatória**: ambientes de execução devem ser segregados:
  - Sessão cega: sem acesso a repo, sem git history, sem memória anterior.
  - Sessão de autoria/revisão: acesso total, usado para design e validação não cega.

### Implicações

1. Ci determinística: testes usam `FakeProvider` (ISSUE-32), sem rede, sem acesso ao repo.
2. Produção: `LLMProvider` concreta (ISSUE-34+) injetada em contexto segregado.
3. Rastreabilidade: cada run registra `prompt_template_sha256` (LS_005) e metadados de run.
4. Auditoria: comportamento cego validável; não confiado apenas a autocontrole do modelo.

## 24. Limitações

Este protocolo possui limitações explícitas:

- documentação não garante isolamento técnico;
- não existe bundler nesta PR;
- não existe leak checker;
- não existe manifest formal;
- não existe sandbox;
- não existe controle automático de ferramentas;
- não existe detecção semântica perfeita;
- não existe garantia de ausência de memória;
- modelos podem inferir corretamente mesmo sem vazamento;
- modelos podem ter conhecimento prévio de casos públicos;
- testes cegos não substituem playtest humano;
- segurança real dependerá das próximas implementações.

Este protocolo não promete segurança perfeita, não afirma que hashes impedem vazamentos, não confunde integridade com confidencialidade, não confunde nome neutro com cegueira completa, não recomenda reescrita silenciosa de evidência, não define schema executável, não define arquitetura de classes, não impõe ferramenta específica, não exige provider específico, não cria dependência de internet, não altera o pipeline atual, não transforma toda revisão em cega e não impede revisões não cegas necessárias.
