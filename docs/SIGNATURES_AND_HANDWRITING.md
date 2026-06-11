# Assinaturas, rubricas e manuscritos P3

## Objetivo

A camada P3 transforma assinatura, rubrica e intervenção manuscrita curta em atributos visuais de personagem. O objetivo é sustentar imersão em P&B, offline first, sem fonte externa, CDN, API ou imagem gerada por IA.

## Diferenças de uso

- **Assinatura completa:** gesto mais longo e orgânico, usado em declarações, cartas, contratos, recibos, orçamentos e responsáveis identificáveis.
- **Rubrica:** gesto curto e compacto, usado como visto, conferência, glifo administrativo ou protocolo. Não é uma assinatura reduzida idêntica.
- **Manuscrito curto:** intervenção humana breve, como anotação à margem, ressalva de rascunho ou palavra solta. Não deve substituir parágrafos nem blocos de texto.

## Campos de blueprint

O perfil continua opcional em cada personagem. Quando ausente, o renderer deriva um perfil determinístico de `id` e `nome`.

Campo consolidado atual:

```json
"assinatura": {
  "estilo": "fluida",
  "pressao": "media",
  "legibilidade": "media",
  "inclinacao": "direita",
  "amplitude": "media",
  "ornamentacao": "sublinhado",
  "variacao": "media",
  "seed": "caso-personagem",
  "override_assinatura_svg": "assets/signatures/personagem/assinatura.svg",
  "override_rubrica_svg": "assets/signatures/personagem/rubrica.svg"
}
```

`assinatura_visual` também é aceito como alias P3. Campos legados (`rubrica_estilo`, `ornamento`, `fluidez`, `variacao` numérica) continuam aceitos para compatibilidade.

## Estilos permitidos

- `fluida`: curvas suaves e baseline variável.
- `angular`: segmentos mais retos e quebras.
- `compacta`: largura menor e poucos gestos.
- `formal`: equilibrada e mais legível.
- `tremida`: irregularidade sutil.
- `apressada`: maior inclinação e variação.
- `ornamental`: laços e inicial destacada quando cabível.
- `minimalista`: gesto econômico, útil para rubricas.

## Regras de manuscrito curto

- Limite recomendado: **até 120 caracteres**.
- Sempre associar personagem por `ANOTACAO_PERSONAGEM_ID` ou `NOTA_MANUSCRITA_PERSONAGEM_ID` quando o campo existir.
- Nunca aplicar manuscrito a corpo longo de documento.
- Não usar manuscrito para dizer ao jogador o que comparar, provar ou concluir.
- Linguagem de solução/gabarito em manuscrito é erro crítico (`HAND_003`).

## Overrides SVG

Overrides manuais continuam com prioridade sobre geração procedural:

- `override_assinatura_svg` / `assinatura_svg_override`;
- `override_rubrica_svg` / `rubrica_svg_override`.

O caminho deve ser relativo ao repositório, apontar para `.svg` existente e não usar `..` nem caminho absoluto.


## Pistas visuais como evidência

Assinaturas, rubricas, grafia, carimbos, marcas e padrões visuais podem participar de uma cadeia investigativa, mas precisam ser intencionais.

Regras:

- semelhança gráfica precisa ser planejada no blueprint;
- personagens diferentes não podem compartilhar grafismo por acidente;
- impressão P&B deve preservar a distinção;
- detalhe não pode ser pequeno demais;
- a pista visual deve sobreviver a impressão doméstica e visualização em celular/tablet;
- pista visual essencial precisa de pelo menos uma confirmação não visual;
- cor isolada não deve ser caminho obrigatório;
- o guia do facilitador deve explicar o que a pista visual permite inferir.

> Pista visual pode acelerar a descoberta, mas não deve ser o único caminho para uma conclusão essencial.

> Consistência visual é parte da cadeia de evidência quando o caso decide tratá-la como evidência; fora disso, é apenas identidade documental.

Quando o caso usar grafismo como evidência, registre a intenção em campos editoriais existentes do blueprint e confirme no PDF real. Fora desse uso, assinatura, rubrica e manuscrito servem para identidade documental, imersão e diferenciação de personagem, não para resolver sozinhos autoria ou mecanismo.

## Checklist visual

1. A assinatura completa e a rubrica do mesmo personagem são diferentes?
2. Personagens do mesmo caso têm SVGs distintos?
3. O SVG funciona em P&B e em impressão?
4. Não há `<text>` ou `font-family` no SVG procedural?
5. A anotação manuscrita é curta e diegética?
6. A anotação não entrega solução, interpretação do autor ou checklist de cruzamento?
7. Override manual, quando usado, é SVG local válido?
8. Se uma semelhança gráfica for pista, ela foi planejada e documentada?
9. A pista visual essencial tem confirmação não visual?
10. Cor, detalhe pequeno ou legibilidade fina não são o único caminho para uma conclusão obrigatória?
