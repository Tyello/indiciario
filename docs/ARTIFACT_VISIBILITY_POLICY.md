# Política de visibilidade de artefatos

## Objetivo

A política de visibilidade responde, de forma pura e determinística, se um papel
pode receber um artefato com determinado `artifact_type`, `visibility`,
`envelope_scope`, `stage` e flags sensíveis. Ela prepara as próximas etapas de
blind bundle sem gerar bundles, copiar arquivos, calcular hashes ou ler conteúdo
de artefatos.

## Relação com o schema do manifest

- O schema do `blind_bundle_manifest` continua sendo a guarda estrutural: enumera
  vocabulário, formato do manifest e regras críticas já expressas no contrato.
- A política é uma guarda semântica inicial: retorna `allow`, `warn` ou `deny`
  com `rule_id`, `reason` e `recommended_action`, inclusive para papéis que o
  schema ainda não especializa.
- A política assume que o manifest recebido já foi carregado e validado por quem
  chama a função; ela não valida YAML nem acessa filesystem.

## Matriz resumida

- `blind_solver`: só recebe material `public_player` ou `derived_report`
  sanitizado, sem solução, gabarito, material futuro, notas privadas, outputs de
  outros agentes, facilitator-only, relatórios privados, learning records ou
  metadata técnica.
- Revisores narrativos, lógicos, de evidência e adversariais: podem receber
  material privado de revisão conforme etapa; solução/gabarito tende a gerar
  `warn`, não `deny`, quando o papel pode precisar validar consistência.
- Revisores visual e de acessibilidade: recebem outputs renderizados, templates,
  metadata técnica e material player-facing; solução/gabarito é negado por
  padrão.
- `gate_evaluator`: pode receber solução, gabarito e learning records em etapas
  compatíveis, porque sua função é avaliação privada final.
- `human_operator`: pode orquestrar estruturalmente os artefatos, mas recebe
  `warn` quando há conteúdo privado ou sensível.
- `technical_reviewer`: recebe schema, template, render output, manifest e
  metadata técnica; solução/gabarito só é tolerado em validação técnica.

## Limitações intencionais

Esta PR não implementa gerador de blind bundle, CLI, leak checker, sanitização,
execução de agentes, OCR, leitura semântica, cálculo real de hash ou validação de
existência de arquivos. Essas capacidades ficam para issues posteriores.

## Próximos passos

A próxima evolução recomendada é a ISSUE-13: gerador manual de blind bundle,
consumindo esta política como guarda semântica sem alterar seu escopo puro.
