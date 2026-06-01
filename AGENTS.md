# AGENTS.md — Guia para Agentes de IA

Este arquivo instrui agentes de IA (Codex, Copilot Workspace, Claude Code e similares)
sobre como atuar neste repositório de forma segura, consistente e alinhada ao projeto.

**Leia este arquivo inteiro antes de executar qualquer tarefa.**

---

## O que é o Indiciários

Indiciários é um gerador de jogos de investigação offline em formato de dossiê com
envelopes. O sistema recebe parâmetros de um usuário (tema, dificuldade, tom), gera
um blueprint estruturado via LLM, valida as regras narrativas do framework e renderiza
documentos em PDF via templates HTML + Playwright/Chromium.

O produto final são PDFs temáticos — e-mails falsos, logs de acesso, boletins policiais,
extratos bancários — que formam um jogo de investigação físico ou digital.

---

## Estrutura do repositório

```
/framework/        ← Arquivos .md com as regras do jogo (NÃO são código)
/templates/        ← Templates HTML dos documentos (viram PDF via renderizador)
/generator/        ← Código Python: modelos, validador, renderizador, pipeline
/examples/         ← Blueprints e PDFs de casos de exemplo (não editar manualmente)
/tests/            ← Testes automatizados
AGENTS.md          ← Este arquivo
README.md          ← Documentação pública do projeto
```

---

## Regras obrigatórias para qualquer tarefa

### 1. Nunca alterar os arquivos de framework sem instrução explícita

Os arquivos em `/framework/*.md` são a fonte da verdade das regras do jogo.
Eles definem o que é um bom caso, o que é um red herring justo, como validar
solvabilidade. **Não modifique esses arquivos** a menos que a tarefa diga
explicitamente "atualizar o framework".

### 2. Nunca quebrar a interface do validador

O arquivo `generator/validator.py` expõe:
- `BlueprintValidator(blueprint, strict=False).validar()` → `ResultadoValidacao`
- CLI: `python validator.py <arquivo.json> [--strict] [--json]`

Qualquer refatoração deve manter essa interface intacta. Se mudar a assinatura,
atualize todos os chamadores e os testes correspondentes.

### 3. Nunca gerar ou commitar dados de caso reais com nomes reais de pessoas

Blueprints e PDFs de exemplo usam **exclusivamente personagens fictícios**.
Não use nomes de pessoas públicas, empresas reais (exceto como referência genérica
de estilo) ou dados pessoais reais em qualquer fixture, teste ou exemplo.

### 4. Sempre rodar o validador antes de marcar uma tarefa como concluída

Se a tarefa envolve geração de blueprint ou modificação no pipeline:

```bash
cd generator
python validator.py exemplo_blueprint.json
```

O resultado deve ser `Risco: Baixo` ou `Risco: Médio-baixo` para a tarefa ser
considerada concluída.

### 5. Templates HTML são autossuficientes

Cada arquivo em `/templates/*.html` deve funcionar isoladamente — CSS inline,
sem dependências externas obrigatórias (fontes do Google são permitidas via CDN
pois são decorativas, não funcionais). Não adicione `<script src="...">` que
quebre a renderização offline via Playwright/Chromium.

---

## Stack técnica

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.11+ |
| Modelos de dados | Pydantic v2 |
| Renderização PDF | Playwright oficial com Chromium |
| LLM | OpenAI API (GPT-4o) ou Anthropic API (Claude) — configurável via env |
| Bot | python-telegram-bot |
| Pagamento | Mercado Pago SDK Python |
| Testes | pytest |
| Linting | ruff |
| Formatação | black |

---

## Convenções de código

### Nomes de variáveis e funções

Use português para nomes de domínio do negócio, inglês para infraestrutura:

```python
# ✅ Correto
def validar_blueprint(blueprint: Blueprint) -> ResultadoValidacao: ...
def gerar_documento(doc: Documento) -> str: ...
class BlueprintValidator: ...

# ✅ Também correto (infraestrutura)
def render_pdf(html: str, output_path: Path) -> None: ...
async def handle_telegram_message(update, context): ...

# ❌ Evitar — mistura aleatória
def validate_personagem(p): ...
def gerar_pdf_document(d): ...
```

### Erros e logging

Use o módulo `logging` padrão. Nunca use `print()` em código de produção.
Erros do validador são retornados como objetos `Erro` — não levante exceções
para falhas de validação esperadas.

```python
# ✅
logger = logging.getLogger(__name__)
logger.warning("Blueprint com risco médio: %s", blueprint.titulo)

# ❌
print(f"AVISO: {mensagem}")
raise ValueError("Blueprint inválido")  # só para erros inesperados
```

### Type hints

Sempre. Sem `Any` quando o tipo é conhecido.

```python
# ✅
def buscar_personagem(id: str, personagens: list[Personagem]) -> Optional[Personagem]:

# ❌
def buscar_personagem(id, personagens):
```

---


### Renderização oficial

Playwright é o renderizador oficial de PDFs do projeto. O `generator/renderer.py` é
a fonte operacional da renderização: ele injeta dados nos templates HTML e chama o
Chromium via Playwright para gerar PDFs. O setup local precisa instalar o browser:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

A orientação portrait/landscape será definida por template/tipo de documento; nesta
fase há smoke test manual para ambas as orientações via `python -m scripts.smoke_playwright_pdf`.

## Como rodar localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar testes
pytest tests/ -v

# Validar um blueprint
python generator/validator.py generator/exemplo_blueprint.json

# Validar em modo estrito (falha em risco Médio)
python generator/validator.py generator/exemplo_blueprint.json --strict

# Saída em JSON (útil para integração)
python generator/validator.py generator/exemplo_blueprint.json --json
```

---

## Variáveis de ambiente necessárias

```bash
# LLM — configure um dos dois
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Qual LLM usar (openai | anthropic)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o

# Telegram
TELEGRAM_BOT_TOKEN=...

# Mercado Pago
MP_ACCESS_TOKEN=...
MP_WEBHOOK_SECRET=...

# Ambiente
APP_ENV=development   # development | production
LOG_LEVEL=INFO
```

Nunca commite valores reais dessas variáveis. Use `.env` local (já no `.gitignore`).

---

## Fluxo principal do pipeline

O agente deve entender esse fluxo antes de modificar qualquer parte:

```
1. Usuário envia parâmetros via Telegram
        ↓
2. pipeline.py monta o prompt com base em 07_PROMPT_GERADOR_DE_CASO.md
        ↓
3. Chamada ao LLM → retorna blueprint em JSON
        ↓
4. Blueprint é parseado via models.Blueprint (Pydantic)
        ↓
5. BlueprintValidator.validar() → ResultadoValidacao
   ├── Risco Alto/Médio-alto → rejeita, pede correção ao LLM (até 2 tentativas)
   └── Risco Médio-baixo/Baixo → avança
        ↓
6. renderer.py injeta dados dos documentos nos templates HTML
        ↓
7. Playwright/Chromium converte cada HTML em PDF
        ↓
8. merger.py agrupa por envelope (E1, E2, dicas, gabarito)
        ↓
9. package_builder.py gera PDFs visuais procedurais quando existirem, manifest.json, print_manifest.json, guia_facilitador.pdf, guia_de_impressao.pdf, qa_report.json, graph_report.json e llm_feedback.json
        ↓
10. Bot envia os arquivos ao usuário no Telegram
```

---

## Tarefas comuns e como abordá-las

### Adicionar um novo tipo de documento ao catálogo

1. Adicionar o valor em `models.TipoDocumento` (enum).
2. Criar o template HTML em `/templates/NN_nome.html` com placeholders `{{VARIAVEL}}`.
3. Adicionar mapeamento em `renderer.py` — qual template usar para o novo tipo.
4. Atualizar `/framework/03_TIPOS_DE_DOCUMENTOS.md` com a nova entrada.
5. Rodar `pytest tests/test_renderer.py`.

### Adicionar uma nova regra de validação

1. Identificar a seção correta em `validator.py` (elenco, documentos, pilares, etc.).
2. Adicionar o método `_verificar_X` ou inserir verificação no método existente.
3. Definir código único para o erro (ex: `NOVO_001`).
4. Adicionar teste em `tests/test_validator.py` com blueprint que viola a regra.
5. Verificar que o blueprint de exemplo ainda passa: `python validator.py exemplo_blueprint.json`.



### Gerar pacote final completo

Use o entrypoint oficial para transformar um blueprint válido no pacote final:

```bash
python -m scripts.build_package examples/showcase_tecnico.json --output output --strict
```

O pacote deve conter envelopes finais, `guia_facilitador.pdf`, `guia_de_impressao.pdf`,
`manifest.json`, `print_manifest.json`, `qa_report.json`, `graph_report.json` e `llm_feedback.json`. Dicas e gabarito, quando
existirem, devem permanecer confidenciais e separados dos arquivos de jogador. O `llm_feedback.json` é artefato técnico interno, não é para jogadores e não entra no `print_manifest.json`.

### Modificar o prompt de geração

O prompt base está em `/framework/07_PROMPT_GERADOR_DE_CASO.md`.
O código em `pipeline.py` lê esse arquivo e interpola as variáveis do usuário.
Se mudar a estrutura do prompt, verifique se o JSON retornado ainda é parseável
por `models.Blueprint`.

### Refatorar o validador

- Mantenha os códigos de erro existentes — eles são referenciados nos logs e testes.
- Não mude a assinatura de `BlueprintValidator.validar()`.
- Após refatoração: `pytest tests/test_validator.py -v` deve passar 100%.

---

## O que NÃO fazer

- ❌ Não remova verificações do validador sem criar uma verificação equivalente.
- ❌ Não altere `NivelRisco` sem atualizar `_calcular_risco()` e os testes.
- ❌ Não commite blueprints com `"pode_gerar": false` na pasta `/examples/`.
- ❌ Não adicione dependências sem atualizar `requirements.txt` e justificar no PR.
- ❌ Não use `time.sleep()` no pipeline — use `asyncio.sleep()`.
- ❌ Não chame a API do LLM diretamente fora de `pipeline.py` — centralize lá.
- ❌ Não exponha o gabarito no material do jogador — essa separação é regra de negócio crítica.

---

## Critério de "tarefa concluída"

Uma tarefa só está concluída quando:

- [ ] `pytest tests/` passa sem falhas.
- [ ] `ruff check generator/` sem erros.
- [ ] `python validator.py generator/exemplo_blueprint.json` retorna risco Baixo ou Médio-baixo.
- [ ] Se a tarefa altera o pacote final: `python -m scripts.build_package examples/showcase_tecnico.json --output output --strict` gera `qa_report.json` com `status: passed`.
- [ ] Nenhuma variável de ambiente real foi commitada.
- [ ] Se modificou framework ou templates: comportamento antigo ainda funciona (sem regressão).

---

## Dúvidas sobre regras do jogo

Se uma tarefa envolver decisão sobre regras narrativas (o que é um red herring justo,
quantos pilares um envelope precisa, quando usar três envelopes), consulte os arquivos
em `/framework/` — especialmente:

- `01_PRINCIPIOS_DO_MODELO.md` — leis invioláveis
- `04_DESIGN_DE_PISTAS.md` — regras de pistas e códigos
- `05_CHECKLIST_SOLVABILIDADE.md` — critério de qualidade final
- `14_GRAFO_DE_PISTAS.md` — grafo lógico e relatório de solvabilidade estrutural
- `15_CONTROLES_DA_LLM.md` — guard rails da LLM e feedback estruturado para correção futura
- `16_GUIA_FACILITADOR.md` — guia confidencial de condução e dicas contextuais
- `17_VISUAL_PROCEDURAL.md` — regras de mapas/cartões visuais gerados por dados

Não tome decisões narrativas por conta própria. Se houver ambiguidade, sinalize
no PR e aguarde instrução humana.
