"""
tests/test_gate_font_fidelity.py

RED (ISSUE-40.2, STEP-02): comprova a lacuna do Canonical Quality Gate atual
(`generator.canonical_quality_gate.evaluate_for_canonical`) quanto a
fallback silencioso de fonte custom -- e define o critério real
(`evaluate_font_fidelity`, nome de critério `"font_fidelity"`, ver
`.ai/runs/ISSUE-40.2/STEP-01_EXECUTION.md`) que ainda não existe.

Reusa infra da 40.1 (`tests/test_font_vendoring.py`): `_montar_html`,
`_MEDIR_FONTE_JS`, fixture `browser`. Os dois testes usam a MESMA montagem
(document_system.css real, com o bloco `@font-face` de uma fonte removido
via monkeypatch em `generator.renderer.DOCUMENT_SYSTEM_CSS_PATH`), para
serem comparáveis:

- `test_gate_currently_misses_font_fallback` PASSA hoje: confirma (via
  medição real do Chromium, mesma técnica de canvas.measureText da 40.1)
  que a fonte de fato cai em fallback nesta montagem, mas o gate atual
  (`evaluate_for_canonical`) não tem nenhum critério `font_fidelity` e não
  reflete o problema -- ele é cego a esse tipo de falha. Isso é o bug.
- `test_gate_catches_font_fallback` FALHA hoje: chama
  `generator.canonical_quality_gate.evaluate_font_fidelity`, que ainda não
  existe (fica para ISSUE-40.2 STEP-03). Vira GREEN só depois de
  implementado.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from generator.pipeline_runner import run_pipeline

from tests.test_font_vendoring import _MEDIR_FONTE_JS, _montar_html, browser  # noqa: F401

MIRANTE_BLUEPRINT_PATH = Path("examples/caso_canonico_iniciante.json")
TEMPLATE_COM_FONTE_QUEBRADA = "01_email.html"
FONTE_REMOVIDA = "DM Sans"

_FONT_FACE_BLOCK_RE = re.compile(
    r"@font-face\s*\{[^}]*font-family:\s*'" + re.escape(FONTE_REMOVIDA) + r"'[^}]*\}\s*",
    re.DOTALL,
)


def _css_sem_fonte(css_original: str) -> str:
    """Remove o bloco @font-face inteiro de `FONTE_REMOVIDA` do CSS real,
    reproduzindo o cenário pré-40.1 (fonte custom sem @font-face local)."""
    css_sem_fonte, n_removidos = _FONT_FACE_BLOCK_RE.subn("", css_original)
    assert n_removidos == 1, (
        f"esperava remover exatamente 1 bloco @font-face de '{FONTE_REMOVIDA}', "
        f"removeu {n_removidos} -- document_system.css mudou de formato?"
    )
    return css_sem_fonte


@pytest.fixture
def css_com_fonte_removida(tmp_path, monkeypatch) -> Path:
    """Copia document_system.css para tmp_path removendo o @font-face de
    `FONTE_REMOVIDA` e aponta o renderer para essa cópia -- mesma montagem
    usada pelos dois testes deste arquivo."""
    import generator.renderer as renderer_module

    css_original = renderer_module.DOCUMENT_SYSTEM_CSS_PATH.read_text(encoding="utf-8")
    css_modificado = _css_sem_fonte(css_original)

    css_path = tmp_path / "document_system.css"
    css_path.write_text(css_modificado, encoding="utf-8")

    monkeypatch.setattr(renderer_module, "DOCUMENT_SYSTEM_CSS_PATH", css_path)
    return css_path


def _fonte_aplicada(browser_, template_nome: str, fonte: str) -> bool:
    """Mede (via Chromium real, mesma técnica canvas.measureText da 40.1)
    se `fonte` foi de fato aplicada ao renderizar `template_nome`."""
    html = _montar_html(template_nome)
    page = browser_.new_page()
    try:
        page.set_content(html, wait_until="load")
        page.evaluate("document.fonts.ready")
        return page.evaluate(_MEDIR_FONTE_JS, fonte)
    finally:
        page.close()


def test_gate_currently_misses_font_fallback(css_com_fonte_removida, browser, tmp_path):
    """Evidencia a lacuna original (RED, STEP-02): com @font-face removido, a
    fonte de fato cai em fallback (confirmado via medição real do Chromium)
    -- mas uma chamada *default* a `evaluate_for_canonical` (sem passar
    `font_fidelity_criterion`) não reflete o problema no veredito.

    Nota histórica (STEP-04, pós-GREEN): o check `font_fidelity` passou a
    existir no STEP-03 (`evaluate_font_fidelity`) e foi conectado a
    `evaluate_for_canonical` no STEP-03_FIX-01 via parâmetro opcional
    `font_fidelity_criterion` -- ver `test_gate_wires_font_fidelity_into_evaluate_for_canonical`.
    Este teste continua válido e não é tautológico: documenta que a lacuna
    original (chamada sem o parâmetro opcional) permanece por design --
    `evaluate_for_canonical` não invoca Playwright por conta própria; quem
    chama o gate precisa montar o critério via `evaluate_font_fidelity` e
    passá-lo explicitamente para o check entrar no veredito."""
    # 1. Confirmar que a montagem de fato quebrou a fonte -- se isso falhar,
    #    o setup do teste está errado, não o gate.
    assert not _fonte_aplicada(browser, TEMPLATE_COM_FONTE_QUEBRADA, FONTE_REMOVIDA), (
        f"{TEMPLATE_COM_FONTE_QUEBRADA}: fonte '{FONTE_REMOVIDA}' deveria estar em "
        f"fallback nesta montagem (setup do teste está errado, não é o gate)"
    )

    # 2. Rodar o gate real sobre um blueprint/manifest normais. O gate atual
    #    não consome o HTML renderizado -- é justamente essa a lacuna.
    from generator.canonical_quality_gate import evaluate_for_canonical

    blueprint = json.loads(MIRANTE_BLUEPRINT_PATH.read_text(encoding="utf-8"))
    result = run_pipeline(
        MIRANTE_BLUEPRINT_PATH,
        "RUN-GATE-FONT-MISS-001",
        output_root=tmp_path / "pipeline-output",
        created_at="2026-06-24T10:00:00Z",
    )
    qualification = evaluate_for_canonical(blueprint, result.manifest, "iniciante")

    nomes_criterios = {c.name for c in qualification.criteria_results}
    assert "font_fidelity" not in nomes_criterios, (
        "gate já tem critério 'font_fidelity' -- se este assert falhar, o "
        "STEP-03 desta issue já foi feito e este teste (RED documentado) "
        "deve ser removido/adaptado no STEP-04, não é regressão real"
    )


def test_gate_catches_font_fallback(css_com_fonte_removida, browser):
    """Critério real da issue: depois do STEP-03, o gate precisa reportar
    falha explícita nomeando template + fonte quando falta o @font-face
    correspondente. Falha hoje (ImportError/AttributeError) porque
    `evaluate_font_fidelity` ainda não existe -- GREEN só depois do
    STEP-03."""
    from generator.canonical_quality_gate import evaluate_font_fidelity

    criterio = evaluate_font_fidelity(
        templates=[TEMPLATE_COM_FONTE_QUEBRADA],
        browser=browser,
    )

    assert criterio.name == "font_fidelity"
    assert criterio.status == "blocker"
    assert TEMPLATE_COM_FONTE_QUEBRADA in criterio.recommendation
    assert FONTE_REMOVIDA in criterio.recommendation


def test_gate_wires_font_fidelity_into_evaluate_for_canonical(
    css_com_fonte_removida, browser, tmp_path
):
    """STEP-03_FIX-01: `evaluate_font_fidelity` não pode ficar como função
    morta -- `evaluate_for_canonical` precisa aceitar o critério pronto
    (parâmetro opcional `font_fidelity_criterion`) e refletir o blocker no
    veredito real do gate (critério de aceite #1 da issue), não só na
    função isolada testada por `test_gate_catches_font_fallback`."""
    from generator.canonical_quality_gate import (
        CuratorQualification,
        evaluate_font_fidelity,
        evaluate_for_canonical,
    )

    criterio = evaluate_font_fidelity(
        templates=[TEMPLATE_COM_FONTE_QUEBRADA],
        browser=browser,
    )
    assert criterio.status == "blocker"

    blueprint = json.loads(MIRANTE_BLUEPRINT_PATH.read_text(encoding="utf-8"))
    result = run_pipeline(
        MIRANTE_BLUEPRINT_PATH,
        "RUN-GATE-FONT-WIRED-001",
        output_root=tmp_path / "pipeline-output",
        created_at="2026-06-24T10:00:00Z",
    )
    qualification = evaluate_for_canonical(
        blueprint,
        result.manifest,
        "iniciante",
        font_fidelity_criterion=criterio,
    )

    nomes_criterios = {c.name for c in qualification.criteria_results}
    assert "font_fidelity" in nomes_criterios
    assert qualification.qualification == CuratorQualification.NOT_READY
    font_criterio_no_resultado = next(
        c for c in qualification.criteria_results if c.name == "font_fidelity"
    )
    assert TEMPLATE_COM_FONTE_QUEBRADA in font_criterio_no_resultado.recommendation
    assert FONTE_REMOVIDA in font_criterio_no_resultado.recommendation
