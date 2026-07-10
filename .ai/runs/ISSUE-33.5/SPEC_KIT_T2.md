# Spec: Reprodutibilidade e temperatura real no Solvability Meter [spec-kit: T2]

## Objetivo
`measure_solvability` deve repassar `temperature` de fato ao `ProviderRequest` do
**solver** (judge continua 0.0), registrar um bloco `reproducibility` no
`SolvabilityReport`/schema, e desfazer a colisão de nome público
`estimate_difficulty` renomeando a versão do meter para
`estimate_difficulty_from_solve_rate`.

## Não-objetivos
- Não mudar limiares SM_003 nem lógica de flags SM_004.
- Não repassar temperatura ao judge (permanece hardcoded 0.0 em `conclusion_judge.py`, já é assim, não tocar).
- Não mudar `playtest_metrics.estimate_difficulty`.
- Não adicionar alias de compatibilidade para o nome antigo.

## Decisões tomadas
- Plumbing da temperatura: campo novo `temperature: float = 0.0` no dataclass
  `LLMBlindSolver` (generator/llm_blind_solver.py), usado em
  `ProviderRequest(..., temperature=self.temperature)` dentro de
  `_call_provider_with_repair` (linha que hoje hardcoda `temperature=0.0`).
  Default 0.0 preserva comportamento de todo chamador existente que não passa o campo.
- `measure_solvability` instancia `LLMBlindSolver(provider=provider, temperature=temperature)`
  em vez de `LLMBlindSolver(provider=provider)`.
- `solver_prompt_sha256`: hash sha256 do arquivo de template do solver
  (`generator/prompts/blind_solver_v1.md`, mesmo path que `LLMBlindSolver` usa),
  calculado uma vez por chamada de `measure_solvability` (fora do loop de runs) —
  é o mesmo hash que o solver reporta em `warnings` como `prompt_template_sha256:...`.
- `judge_prompt_sha256`: capturado do `verdict.prompt_hash` do **primeiro run
  completado com sucesso** dentro do loop (mesmo prompt/versão em todo run, SM_002/RM_004).
- `provider_id`: `provider.provider_id` (atributo do protocolo `LLMProvider`).
- Bloco `reproducibility` é um dict simples anexado ao `SolvabilityReport`
  (dataclass frozen), com chaves: `temperature`, `provider_id`,
  `solver_prompt_sha256`, `judge_prompt_sha256`, `runs_requested`.
- Rename `estimate_difficulty` → `estimate_difficulty_from_solve_rate` em
  `generator/solvability_meter.py`: único consumidor interno é a própria chamada
  em `measure_solvability` (confirmado por grep, ISSUE-33.5.md STEP-01). Sem alias.

## Etapas

### Etapa 1: Rename estimate_difficulty (RM_003)
- FAZ: Em `generator/solvability_meter.py`, renomear `def estimate_difficulty(solve_rate: float) -> str:`
  para `def estimate_difficulty_from_solve_rate(solve_rate: float) -> str:` e atualizar
  a chamada interna em `measure_solvability` (`difficulty_estimate=estimate_difficulty(solve_rate)`
  → `difficulty_estimate=estimate_difficulty_from_solve_rate(solve_rate)`).
  Em `tests/test_solvability_meter.py`, atualizar o import (linha ~34) de
  `estimate_difficulty` para `estimate_difficulty_from_solve_rate`, e a chamada no teste
  parametrizado `test_sm003_difficulty_threshold_table` (linha ~387) para usar o novo nome.
- TOCA: generator/solvability_meter.py; tests/test_solvability_meter.py
- VALIDA COM: `pytest tests/test_solvability_meter.py -q` roda (algumas falhas
  esperadas nesta etapa por causa de etapas seguintes ainda não feitas são OK,
  mas `test_sm003_difficulty_threshold_table` deve passar); `python -c "from generator.solvability_meter import estimate_difficulty"`
  DEVE levantar `ImportError`.
- ESCALA SE: existir qualquer outro chamador de `solvability_meter.estimate_difficulty`
  fora dos dois arquivos acima (novo grep `estimate_difficulty` em generator/ tests/ docs/ framework/
  mostra ocorrência inesperada não prevista nesta spec).

### Etapa 2: Temperatura no LLMBlindSolver (RM_001, parte solver)
- FAZ: Em `generator/llm_blind_solver.py`, adicionar campo `temperature: float = 0.0`
  ao dataclass `LLMBlindSolver` (logo após `max_repair_attempts: int = 1`).
  Em `_call_provider_with_repair`, trocar `temperature=0.0` (dentro da construção de
  `ProviderRequest`) por `temperature=self.temperature`.
- TOCA: generator/llm_blind_solver.py
- VALIDA COM: `pytest tests/test_llm_blind_solver.py -q` — QUANDO nenhum teste
  existente passa `temperature` explicitamente O SISTEMA DEVE manter comportamento
  idêntico (todos os testes existentes continuam verdes, pois default é 0.0).
- ESCALA SE: algum teste existente em tests/test_llm_blind_solver.py já afirma
  `request.temperature == <valor != 0.0>` de forma incompatível com um default 0.0.

### Etapa 3: measure_solvability repassa temperature e monta reproducibility (RM_001 solver, RM_002, RM_004)
- FAZ: Em `generator/solvability_meter.py`:
  1. Trocar `solver = LLMBlindSolver(provider=provider)` por
     `solver = LLMBlindSolver(provider=provider, temperature=temperature)`.
  2. No topo de `measure_solvability` (após a validação SM_001, antes do loop),
     calcular `solver_prompt_sha256` lendo e hasheando (sha256, hexdigest)
     `Path(__file__).parent / "prompts" / "blind_solver_v1.md"` (mesmo path usado
     internamente por `LLMBlindSolver`).
  3. Dentro do loop, após `verdict = judge_conclusions(...)` ter sucesso pela
     primeira vez, guardar `verdict.prompt_hash` numa variável
     `judge_prompt_sha256` (só na primeira vez; runs seguintes não sobrescrevem).
     Inicializar essa variável como `None` antes do loop; se nenhum run tiver
     sucesso a função já levanta `SolvabilityMeterError` antes de chegar no
     ponto de montar o bloco `reproducibility`, então `None` nunca vaza pro
     report final.
  4. No dataclass `SolvabilityReport`, adicionar campo
     `reproducibility: dict[str, object]` (sem default, após `flags` e antes de
     `difficulty_framework_ref`, que tem default — todo campo sem default
     precisa vir antes dos campos com default no dataclass).
  5. Na construção final do `SolvabilityReport` em `measure_solvability`,
     preencher `reproducibility={"temperature": temperature, "provider_id": provider.provider_id,
     "solver_prompt_sha256": solver_prompt_sha256, "judge_prompt_sha256": judge_prompt_sha256,
     "runs_requested": runs}`.
  6. Atualizar a docstring de `measure_solvability` (Args `temperature`) e o
     comentário no topo do módulo (linha ~11, "does not decide approval") que hoje
     diz que a temperatura "not threaded into the solver/judge provider calls" —
     isso deixou de ser verdade para o solver; reescrever essa frase para refletir
     que agora é repassada ao solver e permanece 0.0 fixo só no judge (decisão
     documentada, não bug).
- TOCA: generator/solvability_meter.py
- VALIDA COM: `pytest tests/test_solvability_meter.py -q` — os testes de schema
  (`test_schema_report_serialization_validates`,
  `test_schema_rejects_additional_properties`) vão falhar até a Etapa 4 atualizar
  o schema; isso é esperado nesta etapa.
- ESCALA SE: `JudgeVerdict` não tiver campo `prompt_hash` (checar
  `generator/conclusion_judge.py` — já confirmado que tem; se a etapa encontrar
  assinatura diferente, escalar em vez de adivinhar).

### Etapa 4: Schema solvability_report ganha bloco reproducibility (RM_002)
- FAZ: Em `schemas/solvability_report.schema.yaml`:
  1. Adicionar `reproducibility` à lista `required:` do schema raiz (junto de
     `difficulty_framework_ref`).
  2. Adicionar em `properties:` do schema raiz:
     ```yaml
     reproducibility:
       type: object
       additionalProperties: false
       required:
         - temperature
         - provider_id
         - solver_prompt_sha256
         - judge_prompt_sha256
         - runs_requested
       properties:
         temperature:
           type: number
           minimum: 0.0
           maximum: 2.0
         provider_id:
           type: string
           minLength: 1
           maxLength: 64
         solver_prompt_sha256:
           type: string
           minLength: 64
           maxLength: 64
         judge_prompt_sha256:
           type: string
           minLength: 64
           maxLength: 64
         runs_requested:
           type: integer
           minimum: 1
     ```
  (mesmo estilo dos outros blocos do arquivo — `additionalProperties: false` preservado.)
- TOCA: schemas/solvability_report.schema.yaml
- VALIDA COM: `pytest tests/test_solvability_meter.py -q` — 
  `test_schema_report_serialization_validates` e `test_schema_rejects_additional_properties`
  DEVEM passar.
- ESCALA SE: `python -c "import yaml; yaml.safe_load(open('schemas/solvability_report.schema.yaml'))"`
  levantar erro de parsing (indentação YAML quebrada).

### Etapa 5: Testes novos RM_001/RM_002/RM_004 + regressão
- FAZ: Em `tests/test_solvability_meter.py`, adicionar:
  1. `test_rm001_temperature_reaches_solver_provider_requests_not_judge`: chamar
     `measure_solvability(bundle, expected_conclusions(), provider, runs=1, temperature=0.7)`
     com script de 1 run (`run_pair`); depois de rodar, inspecionar `provider.calls`
     (tupla de `ProviderRequest` na ordem: solver call(s), depois judge call).
     QUANDO `measure_solvability` roda com `temperature=0.7` O SISTEMA DEVE fazer
     com que a primeira `ProviderRequest` (chamada do solver) tenha
     `.temperature == 0.7` E a última `ProviderRequest` (chamada do judge) tenha
     `.temperature == 0.0`.
  2. `test_rm002_reproducibility_block_populated`: rodar `measure_solvability`
     com `runs=2`, `temperature=0.5`; QUANDO o report é retornado O SISTEMA DEVE
     preencher `report.reproducibility["temperature"] == 0.5`,
     `report.reproducibility["provider_id"] == provider.provider_id`,
     `report.reproducibility["runs_requested"] == 2`, e
     `report.reproducibility["solver_prompt_sha256"]`/`["judge_prompt_sha256"]`
     serem strings de 64 hex chars (sha256).
  3. `test_rm004_solver_prompt_sha256_matches_template_file`: computar
     independentemente o sha256 do arquivo
     `generator/prompts/blind_solver_v1.md` (leitura direta em bytes no teste) e
     comparar com `report.reproducibility["solver_prompt_sha256"]` — devem ser
     idênticos (prova que o hash registrado é o hash real do template usado,
     não um valor arbitrário, e é o mesmo texto-base em todo run porque é
     computado uma única vez por bundle/chamada).
  4. Ajustar `test_schema_report_serialization_validates` e
     `test_schema_rejects_additional_properties` se necessário (devem continuar
     funcionando sem mudança, já usam `asdict(report)`).
- TOCA: tests/test_solvability_meter.py
- VALIDA COM: `pytest tests/test_solvability_meter.py -q` — todos os testes
  (antigos + novos) verdes.
- ESCALA SE: `provider.calls` não tiver a ordem solver-depois-judge esperada
  (por exemplo se `run_blind_solver_harness` fizer mais de uma chamada ao
  provider antes do judge em um run sem erro — checar `max_repair_attempts`
  default é 1, então só 1 chamada de solver por run bem-sucedido sem repair).

## Critérios de aceitação globais
1. QUANDO `measure_solvability(..., temperature=X)` roda O SISTEMA DEVE repassar
   `temperature=X` a cada `ProviderRequest` do solver e manter `temperature=0.0`
   em toda `ProviderRequest` do judge — verificado por:
   `pytest tests/test_solvability_meter.py::test_rm001_temperature_reaches_solver_provider_requests_not_judge -q`
2. `SolvabilityReport` serializado (`asdict`) valida contra
   `schemas/solvability_report.schema.yaml` incluindo o bloco `reproducibility`
   — verificado por: `pytest tests/test_solvability_meter.py -q`
3. `from generator.solvability_meter import estimate_difficulty` falha;
   `estimate_difficulty_from_solve_rate` cobre a tabela de limiares — verificado
   por: `pytest tests/test_solvability_meter.py::test_sm003_difficulty_threshold_table -q`
4. Suíte completa verde, sem regressão: `pytest tests/ -q`
5. Lint limpo: `ruff check generator/ scripts/ tests/`
