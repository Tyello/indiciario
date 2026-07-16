# ISSUE-33.8 — Adendo (provider headless, sem API key)

Aplicar sobre `.ai/issues/ISSUE-33.8_SPEC.md` e `.ai/issues/ISSUE-33.8.md` já commitados. Três mudanças:

## 1. Contexto/E4 — configurações de medição

Substituir as duas configurações de E4 por:

| Config | Comando | Nota |
|---|---|---|
| Principal | `--runs 5 --solver-model opus --judge-model sonnet` | variação vem da amostragem padrão do modelo (temperatura é provider-controlled, CC_005) |
| Sensibilidade | `--runs 3 --solver-model opus --judge-model sonnet` (nova execução) | mede estabilidade entre lotes, substituindo o eixo de temperatura |

O relatório E5 registra `temperature: null / provider-controlled` no setup e a limitação na seção 1.

## 2. Fase 2 (sonda de contaminação) — execução sem API

As 3 perguntas rodam via headless, com o mesmo confinamento do provider (fora do repo, sem tools):

```
cd $(mktemp -d)
claude -p "Você conhece o caso 'Uma Noite Sem Flores', da série Sob Investigação? Responda o que souber." --model opus
claude -p "No caso 'Uma Noite Sem Flores' (Sob Investigação), quem é o culpado e qual foi o método?" --model opus
claude -p "No caso 'Uma Noite Sem Flores', cite nomes de personagens secundários que você lembrar." --model opus
```

Colar as três saídas brutas no report do STEP-02 e classificar CONTAMINADO/PARCIAL/LIMPO como já especificado. (Executar num diretório temporário vazio é essencial: numa pasta do repo, a sessão poderia ler o gabarito.)

## 3. Fase 3 (STEP-04) — custo

Trocar "custo aproximado por run em dinheiro" por "consumo de cota da assinatura" (anotar horário e eventual atingimento de limite; recomenda-se rodar fora do horário de desenvolvimento). O relatório E5, seção 1, reporta consumo/viabilidade nesses termos.

Nada mais muda: sonda antes das medições, hipóteses H1–H4, estrutura do relatório e critérios de aceite permanecem.
