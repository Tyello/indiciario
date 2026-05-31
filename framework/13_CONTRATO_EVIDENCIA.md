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
