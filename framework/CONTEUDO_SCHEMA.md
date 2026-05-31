# Schema técnico de `conteudo`

O contrato técnico de renderização é definido por arquivos YAML em
`generator/schemas/*.yaml`. Esses schemas complementam, mas **não substituem**,
`generator/models.py`:

- `models.py` valida a estrutura narrativa do blueprint: personagens, documentos,
  pistas, dicas, papéis e referências cruzadas.
- `generator/schemas/*.yaml` valida o contrato técnico de cada `tipo`/template:
  campos esperados, listas, campos condicionais e campos HTML.
- `generator/validator.py` orquestra as duas camadas antes da renderização.
- `generator/renderer.py` é a fonte operacional da renderização PDF via
  Playwright/Chromium.

## Setup de renderização

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Campos do schema

Cada schema declara:

```yaml
type: email_narrador
template: 01_email.html
description: E-mail narrativo usado como documento do caso.
required:
  - REMETENTE_NOME
optional:
  - ANEXOS
required_when:
  - when:
      field: ANEXOS
      equals: true
    required:
      - TOTAL_ANEXOS
hidden_allowed:
  - COPIA
lists:
  CADA_ANEXO:
    required_when:
      field: ANEXOS
      equals: true
    item_required:
      - NOME_ARQUIVO
html_fields:
  - CORPO_EMAIL
```

### `required`

Campos obrigatórios para o template renderizar sem resíduos técnicos. Ausência,
valor vazio, `None`, `undefined`, `CONTEUDO_GENERICO`, `placeholder`, `tbd` ou
`lorem ipsum` em campo obrigatório gera erro crítico (`CONT_003`).

### `optional`

Campos que podem existir, mas não são sempre necessários para a regra narrativa.
A omissão só é segura quando o template usa seção condicional, fallback ou quando
o campo não deixa placeholder residual no HTML final.

### `required_when`

Lista de regras condicionais. Exemplo: se `ANEXOS: true`, então `TOTAL_ANEXOS` e
`CADA_ANEXO` passam a ser obrigatórios (`CONT_REQUIRED_WHEN_001`). Se a condição
for falsa, esses campos não são exigidos.

### `hidden_allowed`

Campos que podem estar vazios por decisão de apresentação, desde que não deixem
resíduo técnico no HTML final.

### `lists` e `item_required`

Define listas renderizadas por seções Mustache-lite (`{{#LISTA}}...{{/LISTA}}`).
Lista obrigatória ausente/vazia gera `CONT_004`; item sem campo obrigatório gera
`CONT_ITEM_001`.

### `html_fields`

Campos que deveriam carregar HTML mínimo (`<p>`, `<table>`, `<ul>`, `<ol>`,
`<div>` ou `<br>`). Ausência de HTML mínimo gera aviso (`CONT_005`), não bloqueio,
porque pode haver textos curtos legítimos em alguns casos.

## Exemplos

### E-mail com anexos

```yaml
type: email_narrador
template: 01_email.html
required:
  - REMETENTE_NOME
  - REMETENTE_EMAIL
  - DESTINATARIO_EMAIL
  - DESTINATARIO_LABEL
  - DATA_HORA
  - ASSUNTO
  - AVATAR_INICIAL
  - AVATAR_COR
  - COPIA
  - CORPO_EMAIL
  - NOTA_RODAPE
required_when:
  - when:
      field: ANEXOS
      equals: true
    required:
      - TOTAL_ANEXOS
      - CADA_ANEXO
lists:
  CADA_ANEXO:
    required_when:
      field: ANEXOS
      equals: true
    item_required:
      - NOME_ARQUIVO
      - TAMANHO_KB
html_fields:
  - CORPO_EMAIL
```

### Log de acesso

```yaml
type: log_acesso
template: 06_log_acesso.html
required:
  - NOME_SISTEMA
  - DATA_EXPORTACAO
  - TOTAL_REGISTROS
  - REGISTROS
lists:
  REGISTROS:
    required: true
    item_required:
      - DATA
      - HORA
      - ID_USUARIO
      - EVENTO
      - OBSERVACAO
```

### Orçamento

```yaml
type: orcamento
template: 08_orcamento.html
required:
  - NOME_EMPRESA
  - NUMERO_ORCAMENTO
  - ITENS
  - CONDICOES
  - VALOR_TOTAL
required_when:
  - when:
      field: UNIDADES
      equals: true
    required:
      - LISTA_UNIDADES
lists:
  ITENS:
    required: true
    item_required:
      - NUMERO_ITEM
      - NOME_ITEM
      - QUANTIDADE
      - VALOR_TOTAL_ITEM
```

## Regra de omissão narrativa

O schema técnico não deve forçar um elemento narrativo ausente de forma legítima.
Se uma pista, anexo, carimbo ou bloco opcional não existe na história, o blueprint
pode omitir o campo **desde que** o template o trate com seção condicional,
fallback ou campo opcional que não deixe resíduo.

## Regra de placeholder residual

Nenhum HTML/PDF final de produção pode conter:

- `{{CAMPO}}`, `{{#SECAO}}`, `{{/SECAO}}` ou `{{^SECAO}}`;
- `None`, `undefined`, `CONTEUDO_GENERICO`;
- `placeholder`, `tbd` ou `lorem ipsum`.

Em desenvolvimento (`strict=False`), o renderer emite aviso. Em produção ou
pacote final (`strict=True`, padrão de `renderizar_caso`), o renderer lança erro e
bloqueia a geração.
