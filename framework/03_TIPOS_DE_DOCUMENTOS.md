# Catálogo de Documentos para Mistérios Offline

Cada tipo de documento tem função narrativa, especificações visuais e cuidados de design. Varie os tipos dentro de cada envelope para que a investigação pareça orgânica.

---

## Estrutura de cada entrada

- **Função:** por que o documento existe no jogo.
- **Usar quando:** em que tipo de caso ou situação ele faz sentido.
- **Campos obrigatórios:** o que nunca pode faltar.
- **Especificações visuais:** fonte, layout, cores, imperfeições.
- **Cuidados:** riscos de design que podem quebrar a solvabilidade.
- **Emoção esperada:** o que o documento deve provocar no jogador.

---

## 1. Protocolo de investigação `PROTO`

**Função:** orientar o jogador no início do envelope — define o objetivo, o critério de avanço e as regras da experiência.

**Usar quando:** sempre. Todo envelope começa com um protocolo.

**Campos obrigatórios:**
- nome do caso e número do envelope;
- lista de documentos contidos no envelope;
- objetivo do envelope em uma frase;
- critério de validação explícito (os quatro pilares);
- instrução sobre quando abrir o próximo envelope;
- modo de validação (offline: critério de cruzamento / híbrido: QR ou link).

**Especificações visuais:**
- título grande e bold ("Protocolo da investigação"), palavra de destaque em cor de acento;
- blocos de seção com ícone à esquerda em quadrado colorido (pasta, lupa, escudo);
- fonte sans-serif limpa, 13–14pt;
- fundo branco ou creme claro;
- rodapé com nota de experiência offline e créditos.

**Cuidados:** evite frases vagas. "Conecte as pistas" não orienta — "cruze acesso físico, credencial, terminal e ação no intervalo 21h00–22h00" orienta.

**Emoção esperada:** orientação e urgência.

---

## 2. E-mail do narrador suspeito `EMAIL-N`

**Função:** contextualizar o incidente com voz parcial. O narrador tem interesse no resultado — não é neutro.

**Usar quando:** sempre como primeiro documento de conteúdo do Envelope 1.

**Campos obrigatórios:**
```
De: [Nome] <[email@dominio.local]>
Para: [destinatário]
Data: [dd de [mês] de [ano] às hh:mm]
Assunto: [assunto urgente e específico]

[Corpo em parágrafos curtos]

[N] anexos
[ícone] arquivo1.pdf [tamanhoK]  [ícone] arquivo2.pdf [tamanhoK]
```

**Especificações visuais:**
- replicar aparência de cliente de e-mail (Gmail-like) sem copiar logo real;
- fonte sans-serif, 12–13pt, espaçamento generoso entre parágrafos;
- lista de anexos em grid com ícone de PDF e tamanho fictício em KB;
- cor de destaque do cliente compatível com o tema do caso.

**O que o e-mail deve conter:**
- pelo menos uma suspeita plantada em outro personagem;
- pelo menos um dado verdadeiro e verificável nos documentos;
- pelo menos um dado enviesado ou omitido;
- IDs de alguns personagens (não necessariamente todos — deixe um ID desconhecido para criar tensão).

**Cuidados:** o narrador pode mentir por omissão, mas não por fato impossível de detectar. O jogador precisa poder perceber o viés.

**Emoção esperada:** urgência, suspeita inicial sobre o narrador.

---

## 3. E-mail institucional `EMAIL-I`

**Função:** reorientar a investigação no Envelope 2 com voz de autoridade — diretoria, auditoria, polícia ou investigação interna.

**Usar quando:** abertura do Envelope 2 ou virada de investigação.

**Campos obrigatórios:** mesmos do EMAIL-N, mas remetente é cargo/departamento, não pessoa.

**Cuidados:** não revelar a solução. Reformular a pergunta, não respondê-la.

**Emoção esperada:** mudança de perspectiva, nova urgência.

---

## 4. Print de conversa interna `CHAT`

**Função:** criar pressão social, revelar intenção, mostrar versões contraditórias e plantar red herrings. Dá personalidade aos personagens.

**Usar quando:** o caso precisa parecer vivo, com conflito interpessoal visível.

**Campos obrigatórios:**
- nome do grupo visível no topo com número de participantes;
- horário individual por mensagem (HH:MM);
- identificação do remetente por nome e contexto ("Nome - Local/Função");
- pelo menos 4–6 participantes diferentes no mesmo chat.

**Especificações visuais:**
- simular interface de mensagens sem copiar design proprietário;
- fundo escuro (verde oliva ou cinza escuro);
- balões: branco para mensagens de outros, cor de acento para o "usuário";
- nome do remetente em cor distinta por pessoa (máx. 6 cores);
- barra de status simulada (bateria, sinal, WiFi);
- fonte sans-serif, 11–12pt.

**O chat deve conter:**
- pelo menos uma mensagem que parece incriminadora mas tem explicação alternativa;
- pelo menos uma confirmação de álibi cruzável com registro físico;
- pelo menos uma mensagem revelando pressão ou urgência;
- pelo menos uma mensagem que ganha novo sentido após a solução ser revelada.

**Cuidados:** chat não resolve o caso sozinho. Ele planta e pressiona — não substitui prova documental.

**Emoção esperada:** vida e caos — sensação de estar "dentro" do evento.

---

## 5. Mapa ou planta baixa `MAPA`

**Função:** tornar a oportunidade física verificável. Conecta nomes de portas/terminais nos logs com localizações reais.

**Usar quando:** oportunidade física importa — museu, escritório, hospital, escola, pousada.

**Campos obrigatórios:**
- legenda completa com todos os símbolos usados;
- numeração de portas ou zonas (compatível com o log de acesso);
- identificação de áreas restritas, comuns e de exibição;
- posição de câmeras (mesmo que desligadas);
- tipo de autenticação por porta (biometria, crachá, livre);
- sentido do controle de acesso por porta.

**Especificações visuais:**
- máximo 3 cores para categorias de área;
- hachuras para diferenciar em P&B (diagonal, pontilhado, cruzado);
- número da porta em círculo sobre a porta;
- ícone de câmera com triângulo indicando ângulo;
- nomes de salas: sans-serif pequena, legível;
- legenda obrigatoriamente no mesmo documento.

**Regra crítica:** todo terminal, sala ou ponto citado nos logs deve estar no mapa. Toda porta no mapa deve ter número correspondente nos registros.

**Emoção esperada:** orientação espacial, verificação de possibilidades.

---

## 6. Registro de acesso físico ou digital `LOG-ACESSO`

**Função:** provar presença, tentativa de acesso ou ausência no intervalo crítico.

**Usar quando:** sempre em casos com controle de acesso físico ou digital.

**Campos obrigatórios:**
```
Cabeçalho: "DADOS EXPORTADOS DO PERÍODO DE [HH:MM] DE [DATA] ÀS [HH:MM] DE [DATA]"
Exportado em: [data e hora]

DATA | HORA | PORTA | ID DO USUÁRIO | [SENTIDO: ENTRADA/SAÍDA]
```

**Regras de conteúdo:**
- o período exportado deve cobrir o intervalo crítico com margem;
- incluir entradas E saídas quando possível;
- incluir pelo menos uma anomalia intencional (entrada sem saída, acesso fora do turno, porta inesperada);
- todos os IDs devem existir na matriz de personagens ou lista de terceiros;
- não incluir IDs inexistentes.

**Especificações visuais:**
- fonte monoespaçada (`JetBrains Mono` ou `Courier New`);
- cabeçalho com cor primária do tema, texto branco;
- linhas alternadas: branco e cinza muito claro `#F9FAFB`;
- bordas discretas `1px solid #E5E7EB`;
- dados numéricos alinhados à direita;
- anomalias sem destaque visual — o jogador deve encontrar.

**Cuidados:** o log técnico não resolve o caso sozinho. Deve cruzar com comportamento humano (chat, depoimento, escala).

**Emoção esperada:** primeira suspeita concreta.

---

## 7. Escala de turno ou agenda `ESCALA`

**Função:** mostrar quem deveria estar presente, quem estava ausente ou fora do horário regular.

**Usar quando:** horário e oportunidade são parte central da investigação.

**Campos obrigatórios:**
```
Período: [mês/ano até mês/ano]
Cabeçalho: dias do mês
Linhas: turnos por letra de grupo
Legenda de grupos: LETRA A: [Nome 1, Nome 2, ...] — no mesmo documento
```

**Regras de conteúdo:**
- todos os personagens relevantes aparecem em algum grupo;
- o grupo de plantão no dia do crime é identificável;
- pelo menos um personagem está fora do plantão esperado (anomalia = pista);
- a legenda de grupos está no mesmo documento — nunca separada.

**Especificações visuais:**
- cabeçalho de mês: cor primária, texto branco;
- células por grupo: cor suave diferente (A=azul claro, B=verde claro, C=amarelo, D=rosa);
- dia do crime: sem destaque — o jogador calcula;
- fonte sans-serif, células compactas mas legíveis.

**Emoção esperada:** confirmação ou derrubada de álibi.

---

## 8. Manual ou política interna `MANUAL`

**Função:** explicar a regra normal e a exceção que foi explorada pelo crime.

**Usar quando:** o crime depende de uma exceção operacional, fallback, alçada ou procedimento de emergência.

**Campos obrigatórios:**
- título, número de revisão e data;
- assinatura do responsável;
- seção de regra normal;
- seção de exceção ou contingência (a vulnerabilidade);
- seção de sanções.

**Especificações visuais:**
- logo institucional fictício no cabeçalho;
- fonte serif ou sans-serif formal;
- bullet points para cada item de regra;
- assinatura cursiva simulada na base.

**Regra crítica:** o jogador só entende como o crime foi possível depois de ler o manual. A exceção descrita é o mecanismo do crime.

**Emoção esperada:** compreensão da vulnerabilidade explorada.

---

## 9. Contrato, proposta ou apólice `CONTR`

**Função:** provar planejamento anterior ao crime (premeditação).

**Usar quando:** há relação comercial que preparou o terreno para o crime.

**Campos obrigatórios:**
- data **anterior** ao crime;
- partes (razão social, CNPJ fictício, endereço, responsável);
- objeto do contrato;
- valor;
- cláusulas (especialmente as que parecem estranhas);
- assinaturas.

**Regras de conteúdo:**
- a cláusula "estranha" tem função narrativa — conecta o contrato ao crime;
- todo CNPJ e endereço deve ser fictício;
- toda empresa importante citada aqui deve aparecer em outro documento do E2.

**Especificações visuais:**
- cores institucionais (azul escuro ou cinza escuro);
- cabeçalhos de seção em fundo escuro, texto branco, uppercase;
- grid de duas colunas para campos relacionados;
- assinaturas cursivas simuladas.

**Emoção esperada:** descoberta de que o crime foi planejado antes do evento.

---

## 10. Registro de acesso de sistema / log técnico `LOG-SISTEMA`

**Função:** mostrar a ação crítica no sistema — qual operação foi executada, por quem, em qual terminal.

**Usar quando:** o crime envolve operação em sistema digital (crédito, câmeras, autenticação, inventário).

**Campos obrigatórios:**
```
HORA | CLIENTE/OBJETO | EVENTO | USUÁRIO | TERMINAL | JUSTIFICATIVA
```

**Regras de conteúdo:**
- o usuário registrado pode ser diferente de quem fisicamente operou (fallback, credencial usada);
- o terminal deve corresponder a uma localização no mapa;
- a justificativa do evento crítico deve ser estranha ou inconsistente.

**Especificações visuais:** mesmas do LOG-ACESSO — fonte monoespaçada, tabela técnica.

**Emoção esperada:** cruzamento que conecta terminal e usuário ao suspeito.

---

## 11. Boletim policial `BOL`

**Função:** âncora institucional. Confirma fatos objetivos e registra o estado da investigação.

**Usar quando:** Envelope 2, para validar ou contradizer o relato do narrador inicial.

**Campos obrigatórios:**
- número do caso;
- tipo de ocorrência;
- localização, data e hora;
- nome e assinatura do responsável;
- corpo do boletim com: o que foi encontrado, o que foi confirmado, o que segue em investigação.

**Especificações visuais:**
- cabeçalho: logo institucional fictício, fundo azul escuro, texto branco;
- fundo do documento: amarelo muito claro `#FEFCE8`;
- corpo do texto: fonte cursiva simulando caligrafia (Caveat, 13pt);
- campos de identificação preenchidos à mão;
- assinatura e carimbo no rodapé.

**Cuidados:** não revelar a solução. Confirma fatos já verificáveis, registra hipótese de envolvimento interno sem nomear culpado.

**Emoção esperada:** peso institucional, confirmação de que o crime é real e grave.

---

## 12. Depoimento policial `DEPO`

**Função:** versão pessoal do suspeito. Defende, acusa outros e revela detalhes verificáveis.

**Usar quando:** Envelope 2, depois do boletim policial.

**Campos obrigatórios:**
- número do caso;
- nome, data de nascimento do depoente;
- marcação: vítima / suspeito / testemunha;
- corpo em primeira pessoa;
- assinatura do depoente e do coletor;
- data e hora da coleta.

**O depoimento deve conter:**
- defesa plausível do personagem;
- acusação de outro personagem (red herring ou confirmação de trilha);
- pelo menos um detalhe verificável em outro documento;
- pelo menos uma frase que ganha novo sentido após a revelação.

**Especificações visuais:**
- fundo: verde muito claro `#F0FDF4`;
- corpo: fonte cursiva simulando caligrafia;
- campos de identificação em grid com linhas de formulário.

**Emoção esperada:** humanização do suspeito, ambiguidade produtiva.

---

## 13. Cartão de visita com código `CARTAO`

**Função:** pista de destino ou vínculo disfarçada em material aparentemente decorativo ou comercial.

**Usar quando:** Envelope 2, para revelar destino do objeto ou vínculo entre entidades.

**Estrutura obrigatória:**
```
FRENTE (lado de identidade):
  - Logo da empresa fictícia
  - Nome da empresa e slogan
  - Frase com duplo sentido investigativo

VERSO (lado da pista):
  - Elemento com código (grid, sequência, tabela)
  - Frase que orienta indiretamente a leitura
  - QR code decorativo (sem função real em modo offline)
```

**Regras críticas:**
- o código é resolvível apenas com documentos do dossiê — nunca depende de internet;
- a chave de leitura está em outro documento do mesmo envelope ou anterior;
- o cartão **confirma** uma pista, nunca a cria do zero;
- incluir instrução de uso: "CORTAR AO REDOR E DOBRAR AO MEIO".

**Emoção esperada:** descoberta de camada oculta — "isso não era decorativo".

---

## 14. Cadastro de terceiros / controle da guarita `CADAS`

**Função:** listar fornecedores e trabalhadores externos com acesso ao local — suspeitos potenciais ou canais de escoamento.

**Usar quando:** o caso envolve reforma, obra, fornecedor externo ou prestador de serviço.

**Estrutura por fornecedor:**
```
FORNECEDOR N
Razão Social: [nome]
CNPJ: [número fictício]
Endereço: [endereço fictício]
E-mail: [email fictício]
Funcionários para o serviço: [número]
```

**Lista de trabalhadores (tabela):**
```
ID | Nome Completo | Função | Empresa
```

**Regras críticas:**
- IDs de terceiros usam padrão diferente dos IDs internos (ex.: 5 dígitos vs. 2 dígitos);
- número de funcionários declarado bate com a lista;
- pelo menos um trabalhador da lista é relevante para a investigação;
- nenhum ID de terceiro coincide com ID de personagem interno.

**Emoção esperada:** expansão do universo de suspeitos — "havia mais gente com acesso".

---

## 15. Folha de cruzamento `CRUZ`

**Função:** ajudar o jogador a organizar suspeitos, horários, pistas e hipóteses. Vai com o jogador — não contém resposta.

**Usar quando:** sempre, em casos com mais de 4 suspeitos ou múltiplos documentos.

**Posição:** Envelope 1.

**Blocos obrigatórios:**

**Bloco 1 — Suspeitos:**
```
Nome/ID | Motivo aparente | Oportunidade física | Acesso | Benefício | Doc. que acusa | Doc. que descarta
```

**Bloco 2 — Quatro pilares:**
```
Pilar | Documento | Pessoa conectada | Confirmação
```

**Bloco 3 — Linha do tempo:**
```
Hora | Fato aparente | Documento | Contradição | Hipótese
```

**Bloco 4 — Cadeia financeira ou logística (se E2 existir):**
```
Origem | Destino | Valor/Item | Documento | Interpretação
```

**Especificações visuais:**
- logo institucional discreto no cabeçalho;
- tabelas com linhas claras e espaço para preenchimento à mão;
- fonte clara, sem excesso de informação;
- deve parecer uma ficha de trabalho — não um documento de evidência.

**Cuidados:** nenhuma célula pré-preenchida que oriente a solução. A folha organiza, não resolve.

**Emoção esperada:** sensação de controle sobre a investigação.

---

## Equivalência temática

Use esta tabela para sair do viés corporativo e adaptar documentos a outros universos:

| Elemento corporativo | Museu / Arte | Família | Escola | Pousada / Evento |
|---------------------|-------------|---------|--------|-----------------|
| Log de sistema | Livro de visitas | Agenda da casa | Diário de chamada | Lista de hóspedes |
| VPN / MFA | Chave de reserva | Cópia da chave | Crachá de acesso | Cartão de quarto |
| Contrato de parceiro | Carta de doação | Testamento | Contrato de estágio | Contrato de fornecedor |
| Extrato financeiro | Recibo de venda | Extrato bancário | Nota fiscal do evento | Comprovante de reserva |
| Chat interno | Bilhete da equipe | Grupo da família | Conversa da coordenação | Rádio ou recado da recepção |
| Escala de turno | Escala de monitores | Rotina da casa | Grade de aulas | Escala de funcionários |
| Auditoria | Laudo de conservação | Inventário doméstico | Relatório disciplinar | Relatório de ocorrência |
| Mapa de áreas | Planta da galeria | Planta da casa | Mapa da escola | Mapa da pousada |
| Log de acesso | Registro de visitas | Câmera do interfone | Registro de entrada | Controle de reservas |
