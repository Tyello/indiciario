# 15 — Guia de Impressão do Pacote Final

Este documento define a camada operacional de impressão do Indiciário. Ele não cria
novas regras narrativas, pistas ou materiais de facilitador; seu objetivo é explicar
como transformar PDFs finais em um pacote físico claro, separado e seguro.

---

## Objetivo do guia de impressão

O guia de impressão é um documento de produção para gráfica, papelaria ou pessoa
responsável pela montagem física. Ele acompanha o pacote final e descreve:

- quais PDFs existem no pacote;
- quantas páginas cada arquivo possui;
- quais arquivos são dos jogadores;
- quais arquivos são exclusivos do facilitador;
- papel, cor, cópias, orientação e instruções de entrega;
- cuidados para não misturar envelopes, dicas e gabarito.

Ele deve ser compreensível sem conhecer as regras internas do mistério.

---

## Material do jogador vs. material do facilitador

**Material do jogador** inclui apenas documentos investigativos destinados aos
participantes, normalmente organizados em `01_envelope_1.pdf` e
`02_envelope_2.pdf` quando o caso tiver segundo envelope.

**Material do facilitador** inclui dicas, gabarito e qualquer documento que revele
solução, validação ou bastidores. Esse material deve ser marcado como confidencial
e nunca deve ser entregue junto com envelopes de jogador.

Regra inviolável: dicas e gabarito não entram em arquivos com categoria `player`.

---

## Perfis de impressão

O `print_manifest.json` expõe três perfis padrão:

### Econômico

- Sulfite A4 comum.
- Impressão P&B.
- Sem frente e verso.
- Adequado para testes, playtests e uso interno.

### Padrão

- A4 90g ou 120g.
- Colorido recomendado em documentos visuais.
- Mantém boa legibilidade e aparência sem custo excessivo.

### Premium

- Capas ou envelopes físicos em papel kraft.
- Cartões/crachás em papel 180g quando existirem.
- Imagens ou fotografias em papel fotográfico quando existirem.
- Adequado para venda, presente ou sessão especial.

---

## Regra de escala 100%

Todos os arquivos devem ser impressos em escala 100%.

Não usar:

- “ajustar à página”;
- “reduzir para caber”;
- redimensionamento automático;
- margens adicionais impostas pela gráfica sem conferência.

Essa regra preserva alinhamento, leitura, aparência e eventuais documentos que
futuramente tenham recorte, cartões ou medidas específicas.

---

## Não misturar dicas/gabarito

Durante a montagem:

1. Imprimir envelopes de jogador separadamente.
2. Separar dicas e gabarito antes de embalar.
3. Conferir `confidential: true` no `print_manifest.json`.
4. Entregar material confidencial apenas ao facilitador.
5. Conferir a ordem final dos PDFs antes da sessão.

Se houver dúvida, prevalece a separação: todo material confidencial fica fora do
pacote dos jogadores.

---

## Papel recomendado

Recomendação padrão:

- documentos comuns: A4 90g ou 120g;
- dicas/gabarito: A4 comum é suficiente;
- capas/envelopes físicos: kraft ou papel mais rígido quando desejado;
- cartões/crachás futuros: papel 180g ou superior;
- imagens/fotos futuras: papel fotográfico opcional.

O pacote técnico não exige materiais especiais para funcionar; eles apenas elevam a
imersão.

---

## Mapas e orientação paisagem

Quando existirem mapas ou documentos com orientação paisagem, o
`print_manifest.json` deve indicar orientação especial como `Paisagem` ou
`Misto — conferir páginas paisagem`.

A gráfica deve imprimir conforme o arquivo, sem rotacionar manualmente páginas que
já foram exportadas na orientação correta.

---

## Cartões e crachás futuros

Quando o catálogo incluir cartões, crachás ou peças recortáveis, o manifesto de
impressão deverá indicar:

- `cut_required: true`;
- papel recomendado mais rígido;
- instrução de recorte;
- quantidade de cópias;
- destino correto do item.

Nesta PR, a estrutura fica preparada para isso, mas não cria visual procedural nem
expande o catálogo de templates.

---

## Como interpretar `print_manifest.json`

Campos principais:

- `case_title`: nome do caso.
- `total_files`: total de PDFs do pacote final.
- `total_pages`: soma das páginas finais.
- `profiles`: perfis econômico, padrão e premium.
- `files`: lista de instruções por PDF.

Em cada arquivo:

- `file`: nome do PDF no pacote.
- `label`: rótulo humano.
- `pages` e `page_count`: intervalo e total de páginas.
- `copies`: quantidade padrão de cópias.
- `paper`: papel recomendado.
- `color`: orientação sobre cor/P&B.
- `orientation`: retrato, paisagem, misto ou conforme arquivo.
- `duplex`: frente e verso; por padrão, envelopes de jogador usam `false`.
- `cut_required`: se há recorte.
- `confidential`: se deve ficar fora do material dos jogadores.
- `deliver_to`: Jogadores, Facilitador ou Gráfica/Papelaria.
- `instructions`: observação operacional.
