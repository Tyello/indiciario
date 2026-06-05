# Pipeline de design de caso

Este documento define o processo editorial para criar casos investigativos no Indiciário antes de gerar qualquer blueprint JSON.

A principal lição do primeiro playtest é clara: o framework já consegue produzir documentos visualmente interessantes, mas isso não garante que o mistério seja intrigante. O próximo salto é fazer a história nascer forte antes dos documentos.

## Princípio central

Um bom caso não é aquele que esconde a resposta.

Um bom caso é aquele que faz o grupo acreditar em uma resposta plausível antes de perceber a solução correta.

O pipeline de geração deve seguir esta ordem:

```text
história forte
→ verdade oculta
→ mentira plausível
→ suspeitos interessantes
→ curva de suspeita
→ momentos de descoberta
→ plano de envelopes
→ plano documental
→ blueprint JSON
→ PDFs
```

Não iniciar um caso criando documentos finais.

## Antiobjetivo

Evitar que o projeto vire apenas um gerador de documentos bonitos.

Documento bonito não salva história fraca. Template bom não compensa mistério óbvio. Validador estrutural não garante diversão.

O caso só deve avançar para blueprint quando tiver:

- pergunta dramática central;
- motivo humano;
- suspeitos plausíveis;
- mentira aparente;
- virada investigativa;
- momentos de descoberta;
- riscos de obviedade mapeados;
- riscos de injustiça mapeados.

## Etapa 1 — Premissas candidatas

Antes de escolher um caso, gerar múltiplas premissas curtas.

Cada premissa deve conter:

- cenário;
- incidente inicial;
- pergunta dramática;
- motivo humano;
- mecânica investigativa principal;
- tipo de documentos prováveis;
- por que seria divertido jogar.

Formato recomendado:

```markdown
## Premissa 1 — Título provisório

**Cenário:**

**Incidente:**

**Pergunta dramática:**

**Motivo humano:**

**Mecânica investigativa:**

**Documentos prováveis:**

**Por que é divertido:**

**Risco:**
```

Selecionar a premissa mais forte antes de continuar.

## Etapa 2 — Núcleo dramático

Todo caso precisa de núcleo dramático explícito.

```json
"nucleo_dramatico": {
  "pergunta_central": "",
  "verdade_real": "",
  "mentira_aparente": "",
  "tema_humano": "",
  "motivo_emocional": "",
  "virada_principal": "",
  "sensacao_final_desejada": ""
}
```

### Pergunta central

A pergunta central deve gerar curiosidade, não apenas identificar culpado.

Fraco:

```text
Quem desviou o objeto?
```

Melhor:

```text
A peça foi roubada, substituída ou nunca esteve onde todos dizem que estava?
```

Fraco:

```text
Quem sabotou a reunião?
```

Melhor:

```text
O vazamento destruiu os documentos por acidente ou foi criado para impedir uma votação?
```

### Tema humano

Todo caso precisa de tensão humana.

Exemplos:

- ambição;
- medo de exposição;
- reputação;
- dívida;
- inveja profissional;
- lealdade familiar;
- vingança;
- proteção de alguém;
- orgulho ferido;
- humilhação pública.

Sem tema humano, o caso vira auditoria.

## Etapa 3 — Verdade real e mentira aparente

Separar a verdade do que parece verdade.

```markdown
## Verdade real

O que realmente aconteceu, em ordem causal.

## Mentira aparente

O que os jogadores provavelmente vão acreditar no começo.

## Por que a mentira é plausível

Quais evidências sustentam temporariamente essa leitura.

## Como a mentira cai

Quais documentos recontextualizam a hipótese inicial.
```

A mentira aparente não deve ser falsa por truque barato. Ela deve ser uma interpretação plausível dos fatos disponíveis.

## Etapa 4 — Suspeitos e curva de suspeita

Todo suspeito relevante precisa ter função dramática.

Para cada suspeito:

```json
{
  "personagem_id": "",
  "nome": "",
  "papel_publico": "",
  "segredo_ou_pressao": "",
  "motivo_aparente": "",
  "oportunidade_aparente": "",
  "comportamento_estranho": "",
  "evidencia_contra": [],
  "evidencia_que_descarta": [],
  "curva_de_suspeita": {
    "inicio": "baixo|medio|alto",
    "E1": "baixo|medio|alto",
    "E2": "baixo|medio|alto",
    "final": "culpado|complice|descartado|ambíguo"
  }
}
```

### Regra de red herring justo

Um falso suspeito forte precisa ter:

1. motivo aparente;
2. oportunidade aparente;
3. comportamento estranho;
4. evidência concreta que o descarta.

Se não tiver os quatro, é só ruído.

## Etapa 5 — Mecânica investigativa principal

Cada caso canônico deve testar uma mecânica investigativa diferente.

Exemplos:

- logs + mapa + credenciais;
- depoimentos contraditórios + cronologia;
- documento adulterado + versão original;
- ausência significativa de registro;
- rota espacial com falsa oportunidade;
- cadeia financeira indireta;
- objeto físico com dupla interpretação;
- álibi verdadeiro usado para encobrir outra ação.

A mecânica deve ser definida antes dos documentos.

```json
"mecanica_investigativa_principal": {
  "tipo": "depoimentos_contraditorios_e_cronologia",
  "descricao": "O grupo precisa perceber que duas versões não podem coexistir no mesmo horário.",
  "documentos_necessarios": ["depoimentos", "planta", "registro de horário", "mensagem"],
  "risco": "Virar caça-palavras de horário se não houver motivo humano forte."
}
```

## Etapa 6 — Momentos de descoberta

Todo caso precisa planejar seus “aha moments”.

```json
"momentos_de_descoberta": [
  {
    "momento": "O grupo percebe que um registro inicialmente neutro muda de significado.",
    "documentos": [],
    "emocao": "virada lógica",
    "risco": "Se estiver explícito demais, vira dica."
  }
]
```

Um bom momento de descoberta faz o grupo dizer:

> espera, a gente leu isso errado.

Sem momentos de descoberta, o jogo vira leitura burocrática.

## Etapa 7 — Plano de envelopes

Antes de documentos finais, definir o que cada envelope deve causar.

```json
"objetivos_por_envelope": [
  {
    "envelope": "E1",
    "funcao": "levantar hipótese boa, mas incompleta",
    "conclusao_esperada": "",
    "nao_precisa_descobrir_ainda": [],
    "pilares_obrigatorios": [],
    "riscos": []
  },
  {
    "envelope": "E2",
    "funcao": "recontextualizar e confirmar solução final",
    "conclusao_esperada": "",
    "pilares_obrigatorios": [],
    "riscos": []
  }
]
```

### Regra importante

O E1 deve terminar com uma hipótese forte, mas incompleta.

Ruim:

```text
E1 já resolve quase tudo e E2 só confirma.
```

Bom:

```text
E1 revela o mecanismo ou oportunidade. E2 revela motivo, benefício ou recontextualização.
```

## Etapa 8 — Plano documental

Só depois de definir história, suspeitos, virada e envelopes criar documentos.

Para cada documento:

```json
{
  "codigo": "E1-01",
  "tipo": "",
  "visibilidade": "jogador|facilitador|interno",
  "funcao_investigativa": "pista_principal|confirmacao|descarte|red_herring|contexto|ferramenta",
  "o_que_mostra": "",
  "o_que_nao_pode_entregar": [],
  "confirma": [],
  "confirmado_por": [],
  "risco_de_handholding": "baixo|medio|alto"
}
```

Documento de jogador deve mostrar evidência, não dizer como interpretar.

## Etapa 9 — Riscos de obviedade

Antes do blueprint final, listar riscos de caso fácil demais.

```json
"riscos_de_obviedade": [
  {
    "risco": "Um personagem aparece como único decisor em muitos documentos.",
    "impacto": "Jogadores acusam cedo demais.",
    "mitigacao": "Adicionar outros nomes plausíveis no processo ou separar decisão em documentos diferentes."
  }
]
```

Riscos comuns:

- suspeito aparece em documentos demais;
- motivo financeiro explícito cedo demais;
- mapa mostra rota;
- chat parece confissão;
- orçamento vira quadro comparativo;
- um valor é muito diferente dos demais;
- documento diz quais evidências cruzar.

## Etapa 10 — Riscos de injustiça

Também mapear riscos de travamento injusto.

```json
"riscos_de_injustica": [
  {
    "risco": "Jogadores não conseguem ligar código de usuário à pessoa.",
    "impacto": "Travamento no E1.",
    "mitigacao": "Adicionar relação de credenciais ou tornar códigos mais explícitos na dificuldade Iniciante."
  }
]
```

Riscos comuns:

- confirmação está em envelope futuro;
- código não tem tradução acessível;
- pista depende de conhecimento externo;
- documento parece decorativo, mas é obrigatório;
- red herring não tem descarte justo;
- detalhe visual importante é pequeno demais no PDF.

## Etapa 11 — Autocrítica antes do JSON

Antes de gerar blueprint, produzir uma autoauditoria.

```json
"auto_auditoria": {
  "obvio_demais": [],
  "injusto_demais": [],
  "documentos_com_voz_do_autor": [],
  "suspeitos_subutilizados": [],
  "pistas_sem_confirmacao": [],
  "confirmacoes_em_envelope_errado": []
}
```

Se houver problemas graves, corrigir o plano antes de gerar JSON.

## Etapa 12 — Blueprint JSON

Só gerar o blueprint JSON depois que o plano Markdown estiver aprovado.

O blueprint deve ser a execução do design, não o lugar onde se descobre a história.

## Critérios mínimos para avançar para JSON

Antes de gerar o blueprint, o plano precisa responder:

- Qual é a pergunta dramática central?
- Qual é a verdade real?
- Qual é a mentira aparente?
- Quais são os 4 ou 5 suspeitos plausíveis?
- Como cada suspeito cresce ou cai ao longo dos envelopes?
- Quais são os momentos de descoberta?
- O que o E1 resolve?
- O que o E2 recontextualiza?
- Quais documentos são pista, confirmação, descarte, ruído ou ferramenta?
- O que pode ficar óbvio demais?
- O que pode ficar injusto demais?

Se essas respostas não estiverem boas, não gerar JSON.

## Aplicação aos canônicos

### Canônico Iniciante

Atual:

- `examples/caso_canonico_iniciante.json`
- “O Desvio da Reserva Mirante”
- validado em primeiro playtest como fácil, mas com documentos agradáveis.

Papel: régua introdutória.

### Próximo Canônico Intermediário

Não deve ser uma versão difícil do Mirante.

Deve nascer com:

- nova premissa;
- nova mecânica investigativa;
- mais ambiguidade estrutural;
- suspeitos mais equilibrados;
- E2 recontextualizando a leitura do E1;
- menos explicitação de códigos;
- pelo menos dois falsos caminhos fortes.

Usar o template de plano em `docs/canonical_plans/PLANO_CANONICO_INTERMEDIARIO.md` antes de gerar JSON.
