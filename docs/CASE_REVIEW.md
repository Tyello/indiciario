# Case Review Report

O **Case Review Report** é um relatório editorial automático para a Fase 2 do Indiciário 2.0. Ele usa o Case Kernel, contratos de evidência, objetivos por envelope, red herrings e métricas heurísticas de dificuldade para indicar se um caso parece pronto para baseline, revisão humana ou playtest.

Ele não substitui playtest. A função é reduzir achismo antes da mesa, organizando riscos editoriais que um revisor humano deve confirmar no PDF, no pacote final e na sessão de teste.

> Validator responde se o pacote é estruturalmente válido. Case Review responde se o caso parece editorialmente pronto para ser testado.

## Diferença entre validator e Case Review

- **Validator:** verifica estrutura, schema, integridade mínima, códigos, referências e regras editoriais já formalizadas como validação.
- **Case Review:** lê sinais analíticos e heurísticos. Ele pode apontar risco de documento dominante, progressão fraca, E1 pedindo fechamento cedo demais, red herring conclusivo ou dificuldade aparente fora da régua.

O Case Review ainda não bloqueia o build dos pacotes. A opção `--strict` só retorna código de saída diferente de zero quando houver finding crítico no próprio relatório.

## Como rodar

Markdown no stdout:

```bash
python -m scripts.case_review examples/caso_canonico_iniciante.json
python -m scripts.case_review examples/caso_canonico_intermediario.json
```

JSON estruturado:

```bash
python -m scripts.case_review examples/caso_canonico_iniciante.json --format json
```

Gravando arquivo:

```bash
python -m scripts.case_review examples/caso_canonico_iniciante.json --output output/case_review_mirante.md
```

Modo strict:

```bash
python -m scripts.case_review examples/caso_canonico_intermediario.json --strict
```

## Estrutura do Markdown

A saída em Markdown contém:

1. **Resumo** — dificuldade declarada, status, findings críticos e warnings.
2. **Case Kernel** — pergunta pública, conflito central, hipótese do E1, recontextualização do E2, motivação atual e findings `CK_*`.
3. **Solvabilidade** — sinais sobre evidências obrigatórias, dependência de pista única e documento dominante.
4. **Progressão por envelope** — objetivo por envelope, critério de avanço e papel de E1/E2.
5. **Red herrings** — presença, plausibilidade e risco de descrição conclusiva.
6. **Dificuldade** — dificuldade declarada, estimativa heurística e volume documental.
7. **Prontidão para playtest** — status final e interpretação conservadora.

## Códigos CR_*

### Solvabilidade

- `CR_SOLV_001`: poucas evidências obrigatórias.
- `CR_SOLV_002`: risco de documento dominante.
- `CR_SOLV_003`: evidência obrigatória sem documento/envelope associado ou referência documental ausente.
- `CR_SOLV_004`: risco de dependência de uma única pista.

### Progressão por envelope

- `CR_PROG_001`: envelope sem objetivo claro.
- `CR_PROG_002`: E1 parece pedir solução final.
- `CR_PROG_003`: E2 sem recontextualização aparente.
- `CR_PROG_004`: critério de avanço ausente.

### Red herrings

- `CR_RH_001`: red herring ausente.
- `CR_RH_002`: red herring descrito de forma conclusiva.
- `CR_RH_003`: suspeito alternativo sem função investigativa verificável.

### Dificuldade

- `CR_DIFF_001`: dificuldade declarada pode estar subestimada.
- `CR_DIFF_002`: dificuldade declarada pode estar superestimada.
- `CR_DIFF_003`: volume documental incompatível com dificuldade.


## Riscos narrativos futuros

Os códigos abaixo são diretrizes conceituais para evolução futura do Case Review. Eles não são validações implementadas ainda, salvo se um código passar a existir explicitamente no relatório ou no código em versão posterior. Nesta PR, servem para orientar revisão humana, playtest e priorização de futuras heurísticas.

- `CR_NARR_001` — conclusão depende de ausência sem ferramenta de comparação.
- `CR_NARR_002` — mecanismo causal sem âncora documental.
- `CR_NARR_003` — relação necessária entre personagens não documentada.
- `CR_NARR_004` — evidência indireta tratada como evidência direta.
- `CR_NARR_005` — E1 exige abstração alta demais para a ferramenta oferecida.
- `CR_NARR_006` — objeto associado prova presença sem confirmação independente.
- `CR_NARR_007` — registro de sistema usado como prova humana direta sem ressalva.
- `CR_NARR_008` — E2 precisa desfazer convicção errada em vez de recontextualizar descoberta parcial.

Ao revisar manualmente um relatório, trate esses riscos como perguntas editoriais:

- a ausência fica visível sem ser explicada em documento de jogador?
- cada envelope entrega ferramenta investigativa prática, não só intenção autoral?
- motivo, oportunidade e mecanismo aparecem como três camadas distintas da solução?
- ações baseadas em confiança, autoridade ou hábito têm âncora documental anterior à revelação?
- evidências diretas, indiretas/por objeto e sistêmicas estão separadas no plano?

Exemplo de risco narrativo: a solução diz que Marta atraiu Helena para a sala de memória, mas nenhum documento mostra como Helena recebeu esse chamado ou por que responderia a ele. Nesse caso, o problema não é apenas falta de motivo; é mecanismo causal sem âncora documental.

## Status de prontidão

- `READY_FOR_BASELINE`: pronto para gerar ou revisar baseline, com warnings aceitáveis.
- `READY_FOR_PLAYTEST`: sem findings relevantes no relatório heurístico.
- `NEEDS_EDITORIAL_REVIEW`: há quantidade suficiente de warnings para exigir leitura editorial antes de playtest.
- `BLOCKED`: há finding crítico, normalmente referência obrigatória ausente ou inconsistência forte.

A classificação começa conservadora. Warnings não significam que o caso está errado; significam que existe ponto de atenção para revisão.

## Limitações conhecidas

- O relatório não lê PDF renderizado nem detecta problema visual.
- O relatório não mede diversão, ritmo de conversa, travamento real ou frustração.
- Heurísticas de dificuldade usam contagem de documentos, contratos e suspeitos; playtest real prevalece.
- Red herrings são avaliados por campos estruturados, não por interpretação profunda do texto completo.
- O status final não deve ser usado para reabrir decisões canônicas validadas sem evidência nova de PDF, teste ou playtest.

## Por que playtest continua obrigatório

Mistério investigativo é experiência de grupo. Um caso pode estar estruturalmente válido e editorialmente promissor, mas ainda travar na mesa por leitura acumulada, hipótese dominante errada, falta de energia social, uso inesperado das dicas ou documento visualmente cansativo. O Case Review antecipa riscos; apenas playtest confirma jogabilidade.
