"""Configuração comum dos testes.

Garante que a raiz do repositório esteja no sys.path quando os testes rodam em
ambientes locais diferentes, especialmente Windows/PowerShell/Python 3.13.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)

if root_str not in sys.path:
    sys.path.insert(0, root_str)


# Fixtures compartilhadas entre múltiplos arquivos de teste (ISSUE-41.1,
# CI_001): centralizadas aqui em vez de importadas entre módulos de teste
# para evitar F811 (parâmetro de teste redefine o nome importado).
@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    (source / "public/envelope_1").mkdir(parents=True)
    (source / "public/envelope_1/depoimento.md").write_text(
        "Depoimento publico bruto\n", encoding="utf-8"
    )
    (source / "public/envelope_1/recibo.md").write_text(
        "Recibo publico bruto\n", encoding="utf-8"
    )
    (source / "private").mkdir(parents=True)
    (source / "private/solution.md").write_text("Solucao privada\n", encoding="utf-8")
    return source


@pytest.fixture
def output_root(tmp_path: Path) -> Path:
    root = tmp_path / "bundles"
    root.mkdir()
    return root


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        yield navegador
        navegador.close()
