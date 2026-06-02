import json
from pathlib import Path

from generator.models import Blueprint
from generator.pdf_backend import PdfWriter
from generator.validator import BlueprintValidator
from generator.visual_procedural import build_map_svg, build_visual_documents


def make_pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        writer.write(fp)
    return path


def load_canonical_data() -> dict:
    return json.loads(
        Path("examples/caso_canonico_intermediario.json").read_text(encoding="utf-8")
    )


def validation_codes(blueprint: Blueprint) -> set[str]:
    resultado = BlueprintValidator(blueprint).validar()
    return {erro.codigo for erro in resultado.erros + resultado.avisos}


def test_blueprint_antigo_sem_visual_procedural_nao_gera_vp() -> None:
    data = load_canonical_data()
    data.pop("visual_procedural", None)
    blueprint = Blueprint(**data)

    assert blueprint.visual_procedural is None
    assert not any(code.startswith("VP_") for code in validation_codes(blueprint))


def test_mapa_valido_passa_sem_vp() -> None:
    blueprint = Blueprint(**load_canonical_data())

    assert "VP_" not in " ".join(validation_codes(blueprint))


def test_mapa_orientation_portrait_gera_vp_002() -> None:
    data = load_canonical_data()
    data["visual_procedural"]["mapas"][0]["orientacao"] = "portrait"

    assert "VP_002" in validation_codes(Blueprint(**data))


def test_area_dimensoes_invalidas_gera_vp_004() -> None:
    data = load_canonical_data()
    data["visual_procedural"]["mapas"][0]["areas"][0]["w"] = 0

    assert "VP_004" in validation_codes(Blueprint(**data))


def test_conexao_area_inexistente_gera_vp_005() -> None:
    data = load_canonical_data()
    data["visual_procedural"]["mapas"][0]["conexoes"][0]["destino"] = "area_fantasma"

    assert "VP_005" in validation_codes(Blueprint(**data))


def test_marcador_documento_inexistente_gera_vp_006() -> None:
    data = load_canonical_data()
    data["visual_procedural"]["mapas"][0]["marcadores"][0][
        "documento_relacionado"
    ] = "E9-99"

    assert "VP_006" in validation_codes(Blueprint(**data))


def test_marcador_contrato_inexistente_gera_vp_007() -> None:
    data = load_canonical_data()
    data["visual_procedural"]["mapas"][0]["marcadores"][0][
        "contrato_relacionado"
    ] = "C-INEXISTENTE"

    assert "VP_007" in validation_codes(Blueprint(**data))


def test_personagem_visual_inexistente_gera_vp_008() -> None:
    data = load_canonical_data()
    data["visual_procedural"]["personagens"][0]["personagem_id"] = "99"

    assert "VP_008" in validation_codes(Blueprint(**data))


def test_local_visual_documento_inexistente_gera_vp_009() -> None:
    data = load_canonical_data()
    data["visual_procedural"]["locais"][0]["documentos_relacionados"] = ["E9-99"]

    assert "VP_009" in validation_codes(Blueprint(**data))


def test_build_map_svg_retorna_svg_com_areas() -> None:
    blueprint = Blueprint(**load_canonical_data())
    mapa = blueprint.visual_procedural.mapas[0]  # type: ignore[union-attr]

    svg = build_map_svg(mapa)

    assert svg.startswith("<svg")
    assert "Portaria" in svg
    assert "Reserva técnica B" in svg


def test_build_visual_documents_gera_pdfs_com_mock_renderer(
    tmp_path, monkeypatch
) -> None:
    from generator import visual_procedural

    calls: list[tuple[str, Path, bool]] = []

    def fake_renderizar_documento(
        template_nome, dados, output_path, strict=False, landscape=False
    ):
        calls.append((template_nome, output_path, landscape))
        return make_pdf(output_path)

    monkeypatch.setattr(
        visual_procedural, "renderizar_documento", fake_renderizar_documento
    )
    blueprint = Blueprint(**load_canonical_data())

    grupos = build_visual_documents(blueprint, tmp_path, strict=True)

    assert "E1" in grupos
    assert any(path.name.startswith("visual_map_") for path in grupos["E1"])
    assert any(call[0] == "visual_map.html" and call[2] is True for call in calls)
    assert len(grupos["E1"]) == 5


def test_caso_canonico_tem_visual_procedural_com_mapa_landscape() -> None:
    blueprint = Blueprint(**load_canonical_data())

    assert blueprint.visual_procedural is not None
    assert len(blueprint.visual_procedural.mapas) >= 1
    assert blueprint.visual_procedural.mapas[0].orientacao == "landscape"
    assert len(blueprint.visual_procedural.personagens) >= 3
    assert len(blueprint.visual_procedural.locais) >= 1


def test_build_package_inclui_visual_no_envelope_manifest_print_e_qa(
    tmp_path, monkeypatch
) -> None:
    from generator import package_builder

    def fake_renderizar_caso(_blueprint_path, output_dir, strict=True):
        return {
            "E1": [make_pdf(output_dir / "E1-01.pdf")],
            "E2": [make_pdf(output_dir / "E2-01.pdf")],
            "dicas": [],
            "gabarito": [],
        }

    def fake_build_visual_documents(_blueprint, output_dir, strict=True):
        return {
            "E1": [
                make_pdf(
                    output_dir / "visual_map_casa_acervo_mirante_andar_1.pdf", pages=2
                )
            ]
        }

    def fake_render_print_guide(_print_manifest, output_path, strict=True):
        return make_pdf(output_path)

    def fake_render_facilitator_guide(
        _blueprint, output_path, graph_report=None, strict=True
    ):
        return make_pdf(output_path)

    monkeypatch.setattr(package_builder, "renderizar_caso", fake_renderizar_caso)
    monkeypatch.setattr(
        package_builder, "build_visual_documents", fake_build_visual_documents
    )
    monkeypatch.setattr(package_builder, "render_print_guide", fake_render_print_guide)
    monkeypatch.setattr(
        package_builder, "render_facilitator_guide", fake_render_facilitator_guide
    )

    result = package_builder.build_package(
        Path("examples/caso_canonico_intermediario.json"), tmp_path, strict=True
    )
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    print_manifest = json.loads(
        Path(result["print_manifest_path"]).read_text(encoding="utf-8")
    )

    visual_map = next(
        doc for doc in manifest["documents"] if doc["codigo"].startswith("VP-MAPA-")
    )
    assert visual_map["tipo"] == "visual_procedural"
    assert visual_map["envelope"] == "E1"
    assert visual_map["final_file"] == "01_envelope_1.pdf"
    assert visual_map["page_start"] == 2
    assert visual_map["page_end"] == 3
    assert "01_envelope_1.pdf" in {entry["file"] for entry in print_manifest["files"]}
    assert result["status"] == "passed"


def test_mapa_canonico_tem_planta_simples_e_marcadores_curtos() -> None:
    blueprint = Blueprint(**load_canonical_data())
    mapa = blueprint.visual_procedural.mapas[0]  # type: ignore[union-attr]
    nomes = {area.nome for area in mapa.areas}
    labels = [marcador.label for marcador in mapa.marcadores]
    svg = build_map_svg(mapa)

    assert nomes == {
        "Portaria principal",
        "Corredor de carga",
        "Doca lateral",
        "Reserva técnica B",
        "Administração",
        "Vitrine / área pública",
    }
    assert labels == ["Janela operacional", "Credencial / acesso", "Etiqueta RM-17"]
    assert all(len(label) <= 22 for label in labels)
    assert ">1<" in svg
    assert ">2<" in svg
    assert ">3<" in svg
    assert "Legenda" in svg
    assert "Janela operacional" in svg
    assert "Credencial / acesso" in svg
    assert "Planta baixa operacional" in svg
