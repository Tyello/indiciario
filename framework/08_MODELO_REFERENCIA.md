# Modelo de Referência — Padrões e Anti-padrões

Este arquivo registra o que funciona, o que falha e a fórmula reutilizável extraída dos casos de referência analisados. Use como checklist de qualidade narrativa antes de finalizar qualquer caso.

---

## Parte 1 — O que funciona bem

### 1.1 O narrador inicial é um suspeito

O caso começa com um personagem pedindo ajuda — com interesse declarado no resultado. Ele envia documentos, explica o contexto, planta suspeitas nos outros e mistura fatos verdadeiros com viés e omissões.

**Por que funciona:** transforma o primeiro e-mail em documento investigável. O jogador questiona o próprio remetente desde o início, aumentando engajamento imediato.

**Como implementar:**
- o remetente nomeia um suspeito alternativo antes de terminar o e-mail;
- omite pelo menos um dado relevante (sem mentir diretamente);
- revela seu interesse financeiro, profissional ou pessoal;
- lista IDs de alguns personagens, deixando um ou dois desconhecidos.

---

### 1.2 Quatro vetores independentes que convergem

O Envelope 1 funciona melhor quando exatamente quatro evidências de tipos diferentes apontam para o mesmo nome:

| Vetor | Tipo de prova | Documento típico |
|-------|--------------|-----------------|
| Presença física | Estava no local | Registro de acesso, escala |
| Credencial / autenticação | Usou o acesso | Log de VPN, MFA, crachá |
| Dispositivo / terminal | Usou o equipamento | Log de sistema, mapa |
| Ação crítica | Executou a operação | Log de crédito, câmera, auditoria |

Quando os quatro apontam para o mesmo nome, o jogador sente certeza — não suposição.

**Adaptações por tema:**

| Tema | Vetor 1 | Vetor 2 | Vetor 3 | Vetor 4 |
|------|---------|---------|---------|---------|
| Museu | Acesso físico | Escala de turno | Ausência de câmera | Horário de ronda |
| Família | Presença confirmada | Acesso ao item | Motivo financeiro | Contradição no depoimento |
| Escola | Cadastro de entrada | Câmera de corredor | Registro de aula | Testemunho |
| Pousada | Check-in/out | Chave do quarto | Câmera do corredor | Horário do incidente |

---

### 1.3 O mecanismo de exceção como pivô narrativo

O crime acontece quando alguém conhece uma exceção ou fallback operacional melhor que os demais. Exemplos:

- SMS fallback de autenticação;
- token de contingência;
- senha temporária de emergência;
- crachá de visitante ainda ativo;
- gerador em modo econômico desativa alarme;
- alçada manual em caso de queda de sistema;
- portão destrancado durante manutenção.

**Por que funciona:** cria um crime tecnicamente plausível, que exige conhecimento interno e que o jogador só entende depois de ler o manual ou política interna.

**Como implementar:** o manual ou política interna descreve a exceção. O crime usa exatamente essa exceção. O jogador só entende o método depois de ler o manual.

---

### 1.4 Documentos com data anterior ao crime provam premeditação

Contratos, propostas, cadastros e orçamentos datados antes do incidente são as evidências mais fortes do Envelope 2. Eles transformam um crime aparentemente oportunista em operação planejada.

**Regra:** pelo menos um documento do E2 deve ter data anterior ao evento crítico e revelar que a estrutura do crime estava sendo montada.

---

### 1.5 Terceirizados como camada intermediária

Fornecedores externos criam uma categoria de suspeitos que:
- tinham acesso legítimo ao local;
- não são funcionários diretos (dificulta rastreamento);
- podem ser descartados por evidência logística;
- podem ser o canal de escoamento no E2.

**Como implementar:** o cadastro de terceiros lista todos os fornecedores com IDs próprios. A lista de trabalhadores tem nomes e funções. Pelo menos um trabalhador ou empresa é relevante para a investigação — seja como suspeito descartável, seja como canal.

---

### 1.6 O chat interno cria vida sem resolver o caso

Conversas em grupo revelam personalidade, urgência, conflito e intenção — mas nunca substituem prova documental. O chat ideal tem:
- pelo menos uma mensagem que parece incriminadora mas tem explicação alternativa;
- pelo menos uma confirmação de álibi cruzável com registro físico;
- pelo menos uma mensagem que ganha novo sentido após a solução;
- pressão que explica por que alguém fez algo que não deveria.

---

### 1.7 Documentos policiais ancoram credibilidade

O boletim de inspeção e o depoimento confirmam fatos objetivos e introduzem versões alternativas. Eles:
- validam o que o narrador inicial pode ter distorcido;
- registram o estado oficial da investigação;
- permitem comparar a versão pessoal com os fatos documentados.

**O depoimento do suspeito operacional** é o documento mais rico do E2: defende o personagem, acusa outro, revela detalhe verificável e contém frase que ganha novo sentido depois.

---

### 1.8 PAT-01 — Pilar de presença (credencial × regra)

**Definição:** um registro de presença (log de acesso: ator + ponto + horário) só vira prova quando confirmado por um documento de regra independente que declara a credencial pessoal/intransferível e o ponto de acesso exclusivo por autenticação.

**Quando usar:** sempre que um vetor de "credencial / autenticação" da tabela de 1.2 precisar sustentar sozinho a presença de um suspeito — o log nunca basta isolado, precisa do manual ou política que define a regra de exclusividade da credencial.

**Campos:** `pilares_validacao` (`documento_principal` = log, `confirmacao` = manual/política, `personagem_id` = ator); `documentos` do tipo `log_acesso` e `manual`.

**Exemplo:** calibração — E1-03 (log de acesso) × E1-02 (manual da porta biométrica), caso `examples/caso_referencia_uma_noite_sem_flores.json`.

**Modo de falha:** log sem documento de regra que confirme exclusividade da credencial → a presença vira coincidência, não prova (cross-ref 2.7 — período do log que não cobre o evento crítico agrava o mesmo problema). Aprofunda 1.2 (vetor credencial/autenticação) e 1.3 (mecanismo de exceção).

---

### 1.9 PAT-02 — Descarte por motivo-sem-oportunidade

**Definição:** o suspeito aparente tem motivo e esteve presente, mas um documento prova que não teve oportunidade física — posto ou credencial não o colocam no local durante o intervalo crítico.

**Quando usar:** para descartar um suspeito plausível sem depender de afirmação do facilitador — o descarte precisa nascer de um documento que o jogador possa cruzar sozinho.

**Campos:** `red_herrings` (categoria `motivo_sem_oportunidade`); `contratos_evidencia` (tipo `descarte`) ancorado num documento de descarte.

**Exemplo:** calibração — Rui, com posto fixo na sala de segurança, sem registro de passagem pela galeria no intervalo crítico, caso `examples/caso_referencia_uma_noite_sem_flores.json`.

**Modo de falha:** descarte sem documento que o ancore vira afirmação do facilitador, não dedução do jogador (tema adjacente a 2.3 — vínculo por sobrenome sem confirmação: ambos falham por faltar o terceiro documento que fecha a inferência).

---

### 1.10 PAT-03 — Pista-código offline (elemento em A, chave em B)

**Definição:** um código impresso num documento (etiqueta, sequência, cor→hex) só se resolve cruzando com a chave de decodificação presente em outro documento — pista não óbvia, 100% offline.

**Quando usar:** quando o caso precisa de uma pista de dedução pura, sem depender de ferramenta externa, mas que não seja resolvível olhando só o documento onde o código aparece.

**Campos:** `codigos` (`documento` = onde o código aparece, `chave_em` = onde a chave de decodificação aparece, `elementos`); os dois `documentos` que carregam código e chave.

**Exemplo:** calibração — `#7F004B` no orçamento de corte cruzado com o catálogo da Arcano (E2-08), caso `examples/caso_referencia_uma_noite_sem_flores.json`.

**Modo de falha:** chave no mesmo documento do código deixa de ser dedução — vira leitura direta (cross-ref 2.4 — critério misto em código sem aviso: mesma família de erro, código que não exige cruzamento real).

---

### 1.11 PAT-04 — Virada de envelope: suspeito presente / objeto ausente

**Definição:** o Envelope 1 fecha num suspeito plausível e presente; o Envelope 2 vira a leitura ao constatar que o objeto do crime já não está onde o suspeito está, reorientando a pergunta de "quem parece" para "como saiu / para onde foi".

**Quando usar:** para dar ao E2 uma razão de existir além de confirmar o E1 — o segundo envelope precisa mudar a pergunta central, não só adicionar prova ao mesmo nome.

**Campos:** `objetivos_por_envelope` (E1 = identificar suspeito; E2 = culpado + destino do objeto); `conflito_central.verdade_aparente` vs. `verdade_real_resumida`; salto documentado em `cadeia_financeira`.

**Exemplo:** calibração — E1 nomeia a credencial interna que abriu a porta; E2 segue a obra pela logística de escoamento, caso `examples/caso_referencia_uma_noite_sem_flores.json`. Adjacente a 1.4 (documentos com data anterior provam premeditação), mas PAT-04 é sobre a reorientação da pergunta entre envelopes, não sobre a prova documental em si.

**Modo de falha:** E2 que só confirma o E1 sem virar a leitura → o segundo envelope não justifica sua existência.

---

## Parte 2 — Anti-padrões a evitar

### 2.1 ❌ ID inexistente em código

**Erro:** `CHAVE 09/14/22/31` onde o ID 14 não existe na matriz de personagens.

**Impacto:** jogadores que tentam decodificar encontram um beco sem saída. Gera frustração e sensação de erro do autor.

**Correção:** antes de criar qualquer código com números, listar todos os IDs existentes e verificar que cada elemento do código pertence a alguém ou tem explicação documental explícita.

---

### 2.2 ❌ Entidade no extrato sem âncora

**Erro:** o extrato de repasses cita "Rota 14 Transportes" como destino de R$ 88.000, mas nenhum outro documento menciona essa empresa.

**Impacto:** jogadores procuram um documento que não existe, assumem que perderam algo ou desistem do fio.

**Correção:** toda entidade relevante no extrato aparece em pelo menos um outro documento (orçamento, cartão, cadastro, contrato).

---

### 2.3 ❌ Vínculo por sobrenome ou iniciais sem confirmação

**Erro:** "Bruno Barros" em um documento e "L. Barros" em outro — o vínculo depende de inferência de parentesco.

**Impacto:** jogadores podem chegar à conclusão certa pelo motivo errado, ou não chegar porque não assumem o parentesco.

**Correção:** adicionar um terceiro documento com a ligação explícita — endereço compartilhado, e-mail de mesmo domínio, referência direta, conta bancária.

---

### 2.4 ❌ Critério misto em código sem aviso

**Erro:** `AR-31-18-22-12` usa IDs de pessoas, mas `MB-09-14-22-31` mistura ID com endereço sem indicar a diferença.

**Impacto:** jogadores aplicam o critério aprendido no primeiro código ao segundo e chegam a conclusão errada.

**Correção:** padronizar critério em todos os códigos do mesmo caso, ou sinalizar documentalmente quando o critério muda.

---

### 2.5 ❌ Personagem técnico com papel ambíguo

**Erro:** Thomaz processa o desembolso automaticamente, mas o log o mostra como executor. Jogadores confundem responsabilidade operacional com autoria.

**Correção:** o boletim ou relatório técnico explicita que o processamento foi automático ou consequência de ação prévia. O gabarito diferencia executor, processador automático e planejador.

---

### 2.6 ❌ Contagem de documentos inconsistente

**Erro:** o protocolo lista "3 e-mails, 1 print, 1 mapa, 3 logs e 1 relatório" (9 documentos), mas o envelope tem 11 páginas.

**Correção:** contar os documentos após escrever todos e ajustar o protocolo para refletir a contagem real.

---

### 2.7 ❌ Período do log não cobre o evento crítico

**Erro:** o log é exportado das 09h50 às 17h04, mas o crime ocorreu às 15h15 e a energia caiu às 15h00. O log existe, mas o intervalo do crime está mal representado.

**Correção:** o período de exportação do log sempre cobre o intervalo crítico completo com margem antes e depois.

---

### 2.8 ❌ Escala sem legenda de nomes no mesmo documento

**Erro:** a escala mostra grupos A, B, C, D, mas a legenda de nomes está em outro documento ou não existe.

**Correção:** a legenda de grupos é parte obrigatória do documento da escala.

---

## Parte 3 — Fórmula reutilizável

> Uma operação aparentemente legítima foi aprovada por alguém que parecia culpado.
> Mas a investigação revela que a credencial foi preparada, a exceção foi explorada
> e o benefício já tinha destino antes do incidente.

Essa fórmula funciona para:

| Tema | Aplicação |
|------|-----------|
| Fraude de crédito | Credencial usada via fallback, lote fraudulento aprovado, dinheiro para empresa de fachada |
| Roubo de obra | Acesso durante janela de câmeras offline, escoamento por fornecedor, venda em galeria clandestina |
| Sabotagem de sistema | Deploy explorado para alterar regra, benefício para concorrente ou comprador |
| Desvio de prêmio | Alçada manual usada para liberar bônus indevido, repasse para conta intermediária |
| Fraude de inventário | Item dado como perdido, ressurgindo em venda paralela via fornecedor de confiança |
| Crime logístico | Carga desviada durante transporte, motorista pagado, nota fiscal com destino falso |

---

## Parte 4 — Checklist específico para casos técnicos (fintech, TI, sistema)

- [ ] Existe glossário com termos técnicos explicados.
- [ ] O jogador entende a regra normal de operação.
- [ ] O jogador entende a exceção ou fallback que existe.
- [ ] O crime explora especificamente a exceção.
- [ ] O log técnico não resolve o caso sozinho.
- [ ] O log técnico cruza com comportamento humano (chat, acesso físico, escala).
- [ ] A motivação aparece em documentos não técnicos (contrato, extrato, depoimento).
- [ ] O beneficiário aparece antes do E2 ou é introduzido de forma justa no E2.
- [ ] O gabarito diferencia executor, planejador e beneficiário explicitamente.
- [ ] A folha de cruzamento tem coluna para acesso, credencial, terminal e ação.

---

## Parte 5 — Checklist específico para casos físicos (museu, pousada, família)

- [ ] O mapa mostra todas as salas e portas relevantes com numeração.
- [ ] O registro de acesso físico cobre o intervalo crítico.
- [ ] A escala de turno confirma ou nega presença de cada personagem.
- [ ] O objeto roubado tem âncora documental (apólice, inventário, folder, laudo).
- [ ] O caminho de escoamento do objeto é documentado no E2.
- [ ] O destino final do objeto está identificado (galeria, colecionador, armazém).
- [ ] Não há personagem com acesso físico completo e sem álibi além do culpado.
- [ ] O boletim policial confirma a ausência do objeto e a ausência de arrombamento.
