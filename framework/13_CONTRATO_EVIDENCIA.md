# Contrato de Evidência

**[INTERNO] — usado no blueprint e na validação.**

O contrato de evidência é uma unidade mínima de solvabilidade: ele declara qual conclusão o jogador deve conseguir tirar, em que fase essa conclusão deve estar disponível e quais documentos sustentam a conclusão sem depender de chute.

Ele não substitui a matriz de pistas nem o gabarito. Ele torna explícito o vínculo entre documentos, conclusão e avanço narrativo.

---

## 1. Por que existe

Um caso pode ter documentos bonitos e ainda assim ser injusto se a conclusão depender de interpretação livre demais. O contrato de evidência existe para impedir três falhas comuns:

1. **Conclusão sem prova:** o gabarito afirma algo que nenhum documento comprova.
2. **Prova única frágil:** um documento sugere uma leitura, mas nada confirma por outro caminho.
3. **Spoiler fora de fase:** o jogador precisa de um documento de envelope futuro para resolver uma pergunta do envelope atual.

---

## 2. Pista x conclusão

**Pista** é um sinal local: uma data, um nome, um valor, uma contradição, um registro de acesso, uma assinatura, uma ausência.

**Conclusão** é o resultado investigativo produzido ao cruzar pistas: quem teve oportunidade, qual alternativa foi descartada, quem se beneficiou, qual cadeia logística é plausível, ou qual solução final fecha o caso.

Um contrato de evidência descreve a conclusão e amarra essa conclusão a documentos concretos.

---

## 3. Prova principal e confirmação independente

**Prova principal** é o documento que sustenta diretamente a conclusão.

**Confirmação independente** é outro documento que confirma a mesma conclusão por caminho diferente. Ela deve reduzir ambiguidade, não apenas repetir a mesma informação com outra diagramação.

Exemplo: um log de acesso pode provar presença; uma escala de turno, mapa, recibo ou depoimento pode confirmar que essa presença importa.

---

## 4. Como evitar chute

Para evitar chute, uma conclusão obrigatória deve responder:

- qual documento aponta a conclusão;
- qual documento confirma por caminho independente;
- quais alternativas são descartadas;
- o que o jogador deve fazer para chegar lá;
- em qual fase a conclusão deve estar resolvível.

Se a resposta correta parece apenas “mais provável”, mas não “melhor comprovada”, o contrato está fraco.

---

## 5. Validação de avanço por envelope

A fase do contrato define o limite documental permitido:

- contrato de `E1` só pode depender de documentos de `E1`;
- contrato de `E2` pode depender de `E1` e `E2`, mas não de `E3` ou posterior;
- contrato de `E3` pode depender de `E1`, `E2` e `E3`;
- contrato `final` pode usar qualquer envelope existente.

A regra protege a progressão. O jogador não deve precisar abrir um envelope futuro para resolver uma pergunta anterior.

---

## 6. Estrutura recomendada no blueprint

```json
{
  "id": "C-E1-01",
  "conclusao": "A credencial usada estava presente na sala durante a janela crítica.",
  "fase": "E1",
  "tipo": "oportunidade",
  "prova_principal": "E1-04",
  "confirmacao_independente": "E1-06",
  "descarta_alternativas": ["E1-05"],
  "personagens_afetados": ["01"],
  "acao_esperada_jogador": "cruzar log de acesso com mapa de sala",
  "risco_ambiguidade": "baixo",
  "obrigatoria_para_avanco": true
}
```

---

## 7. Exemplo inválido

```json
{
  "id": "C-E1-02",
  "conclusao": "O beneficiário final já pode ser identificado no Envelope 1.",
  "fase": "E1",
  "tipo": "beneficiario",
  "prova_principal": "E2-08",
  "confirmacao_independente": "E1-06",
  "descarta_alternativas": [],
  "personagens_afetados": ["03"],
  "acao_esperada_jogador": "adivinhar quem recebeu o valor",
  "risco_ambiguidade": "alto",
  "obrigatoria_para_avanco": true
}
```

Problemas: a prova principal está em envelope posterior, a ação esperada sugere chute e o risco de ambiguidade é alto para avanço obrigatório.

---

## 8. Contrato final

O contrato `final` integra o caso inteiro. Ele pode usar qualquer envelope existente, mas ainda precisa de prova principal e confirmação independente. A solução final não deve ser uma lista de palpites; deve ser a menor explicação que satisfaz todos os contratos obrigatórios anteriores.

---

## 9. Avanço obrigatório x revelação no E2

`obrigatoria_para_avanco: true` significa que o contrato destrava a abertura do próximo envelope. Por isso, a `prova_principal` de um contrato obrigatório precisa estar no envelope atual: no gate E1→E2, a prova principal fica em E1.

A revelação do E2 e a solução final não são “avanço”; são destino investigativo. Modele esses passos como contrato `fase: "E2"` com `tipo: "recontextualizacao"` e contrato `fase: "final"` ou `tipo: "solucao_final"`, ambos com `obrigatoria_para_avanco: false`. Contratos E2 e final podem usar `prova_principal` em E2, conforme as regras das seções 5 e 8.

Essa separação evita ER_007: contrato obrigatório de E1 com prova em E2 é spoiler fora de fase; revelação/solução do E2 marcada como obrigatória para avanço transforma destino em gate e vaza informação.

Exemplo válido de par:

```json
[
  {
    "id": "C-E1-GATE-01",
    "conclusao": "A hipótese parcial do E1 identifica a oportunidade operacional durante a janela crítica.",
    "fase": "E1",
    "tipo": "oportunidade",
    "prova_principal": "E1-03",
    "confirmacao_independente": "E1-05",
    "descarta_alternativas": ["E1-06"],
    "personagens_afetados": ["02"],
    "acao_esperada_jogador": "cruzar log de acesso com escala do turno",
    "risco_ambiguidade": "baixo",
    "obrigatoria_para_avanco": true
  },
  {
    "id": "C-FINAL-01",
    "conclusao": "A solução final combina oportunidade, método e benefício revelado no E2.",
    "fase": "final",
    "tipo": "solucao_final",
    "prova_principal": "E2-04",
    "confirmacao_independente": "E2-07",
    "descarta_alternativas": ["E1-06", "E2-02"],
    "personagens_afetados": ["02", "04"],
    "acao_esperada_jogador": "recontextualizar a oportunidade do E1 com o benefício documental do E2",
    "risco_ambiguidade": "baixo",
    "obrigatoria_para_avanco": false
  }
]
```
