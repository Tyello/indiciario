# 17 — Visual Procedural Controlado

Este arquivo define a primeira camada de visual procedural do Indiciário: mapas e cartões visuais gerados por dados estruturados do blueprint, sem imagem externa e sem geração por IA.

---

## Objetivo

O visual procedural existe para complementar a investigação com peças visuais simples, legíveis e reproduzíveis. Ele deve ajudar o jogador a entender logística, oportunidade, relações espaciais, personagens ou locais relevantes para a solução.

Nesta versão, o visual procedural não é uma etapa artística premium. Ele é uma camada operacional: transforma coordenadas, rótulos, cores, ícones e referências narrativas em SVG/HTML local que pode ser renderizado em PDF pelo pipeline oficial.

---

## Visual gerado por dados vs. imagem gerada por LLM

**Imagem gerada por LLM** é uma imagem sintetizada por um modelo generativo a partir de texto. Ela pode criar detalhes não controlados, inconsistências visuais ou elementos que não existem no blueprint.

**Visual gerado por dados** é construído por regras determinísticas a partir de campos explícitos do blueprint. Um mapa procedural, por exemplo, nasce de áreas com `x`, `y`, `w`, `h`, conexões e marcadores. Um cartão de personagem nasce de `personagem_id`, silhueta, ícone, cor e detalhes.

Para o Indiciário, a diferença é crítica: o visual precisa ser auditável, offline, repetível e narrativamente controlado. Nenhum elemento visual deve introduzir pista nova fora do blueprint.

---

## Por que SVG/HTML

SVG e HTML são usados porque:

- funcionam offline;
- são texto versionável e revisável em PR;
- permitem impressão em PDF via Playwright/Chromium, o renderizador oficial do projeto;
- dispensam PNG/JPG, API externa e chamadas a modelos de imagem;
- mantêm acessibilidade básica em P&B com contraste, rótulos e formas simples;
- permitem que testes validem estrutura, referências e presença de elementos.

---

## Visuais suportados nesta versão

### 1. Mapa simples de um andar

Mapa em SVG com canvas único, áreas retangulares, conexões, marcadores e legenda. Serve para explicar logística, acesso, oportunidade e circulação dentro de um espaço narrativo.

### 2. Cartão de personagem

Cartão visual com identificação do personagem, silhueta abstrata, ícone, cor e detalhes curtos. Serve para apoiar memória de elenco e destacar características úteis ao raciocínio.

### 3. Cartão de local

Placa/cartão visual de local com nome, tipo, ícone, descrição e documentos relacionados. Serve para reforçar locais narrativamente importantes, como sala, depósito, doca, portaria ou reserva técnica.

---

## Limites

- Não é planta arquitetônica perfeita.
- Não é ilustração realista.
- Não substitui design manual premium.
- Não representa múltiplos andares.
- Não é editor visual.
- Não cria fotografia, pintura, retrato realista ou render 3D.

---

## Regras obrigatórias

1. Mapas são sempre `landscape`.
2. Nenhum visual pode depender de imagem externa.
3. Não usar fundo fotográfico.
4. Não usar QR code, link ou URL como elemento de jogo.
5. O visual precisa complementar a história, não decorá-la de forma genérica.
6. Todo elemento visual precisa ter função narrativa.
7. Marcadores e locais que referenciam documentos devem apontar para documentos existentes.
8. Marcadores que referenciam contratos devem apontar para contratos de evidência existentes.
9. Cartões de personagem devem apontar para personagens existentes.
10. O material visual de jogador não pode ser misturado com gabarito, dicas ou guia confidencial.

---

## Critério de qualidade

Um visual procedural é adequado quando o jogador consegue responder: “por que este mapa/cartão está no dossiê?” Se a resposta for apenas “para ficar bonito”, o visual deve ser removido ou conectado a uma função narrativa real.
