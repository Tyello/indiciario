from __future__ import annotations

from pathlib import Path

from scripts.visual_sanity_check import check_blueprint, check_pdf_text


def _blueprint_with_html(html: str, *, tipo: str = "manual", titulo: str = "Documento") -> dict:
    return {
        "documentos": [
            {
                "codigo": "E1-01",
                "titulo": titulo,
                "tipo": tipo,
                "conteudo": {"CORPO_CARTA": html},
            }
        ]
    }


def _codes(issues):
    return {issue.code for issue in issues}


def test_tabela_sem_colgroup_gera_warning() -> None:
    blueprint = _blueprint_with_html(
        "<table class='table-admin'><thead><tr><th>Horário</th><th>Entrada</th></tr></thead>"
        "<tbody><tr><td>15h30</td><td>Roda</td></tr></tbody></table>"
    )

    issues = check_blueprint(blueprint)

    assert "VIS_TABLE_001" in _codes(issues)
    assert next(issue for issue in issues if issue.code == "VIS_TABLE_001").severity == "warning"


def test_tabela_com_muitas_colunas_gera_warning() -> None:
    blueprint = _blueprint_with_html(
        "<table class='table-admin'><colgroup><col><col><col><col><col></colgroup>"
        "<thead><tr><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th></tr></thead>"
        "<tbody><tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td></tr></tbody></table>"
    )

    issues = check_blueprint(blueprint)

    assert "VIS_TABLE_002" in _codes(issues)


def test_persona_em_documento_de_jogador_gera_erro() -> None:
    blueprint = _blueprint_with_html("<p>Registro interno/persona 10031</p>")

    issues = check_blueprint(blueprint)

    assert "VIS_TEXT_001" in _codes(issues)
    assert next(issue for issue in issues if issue.code == "VIS_TEXT_001").severity == "error"


def test_folha_de_apoio_com_poucas_linhas_em_branco_gera_warning() -> None:
    blueprint = _blueprint_with_html(
        "<table class='table-support'><colgroup><col><col><col><col></colgroup>"
        "<thead><tr><th>Horário</th><th>Fonte</th><th>Documento</th><th>Anotação</th></tr></thead>"
        "<tbody><tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>"
        "<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr></tbody></table>",
        tipo="folha_cruzamento",
        titulo="Folha de apoio da apuração",
    )

    issues = check_blueprint(blueprint)

    assert "VIS_TABLE_003" in _codes(issues)


def test_texto_simulado_de_pdf_com_palavras_coladas_gera_warning() -> None:
    issues = check_pdf_text("Nara BittencourtMediadora chegou antes da roda.")

    assert "VIS_TEXT_002" in _codes(issues)
    assert next(issue for issue in issues if issue.code == "VIS_TEXT_002").severity == "warning"


def test_blueprint_valido_do_iniciante_b_passa_sanity_check() -> None:
    path = Path("examples/caso_canonico_iniciante_b.json")
    import json

    blueprint = json.loads(path.read_text(encoding="utf-8"))

    assert check_blueprint(blueprint) == []
