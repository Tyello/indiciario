import json
from pathlib import Path

from generator.clue_graph import analyze_clue_graph, build_clue_graph, write_graph_report
from generator.models import Blueprint, ContratoEvidencia
from tests.test_generator_validator import blueprint_valido, _documento
from generator.models import Envelope, TipoDocumento


def _contrato(
    id_: str = "C-FINAL-01",
    *,
    fase: str = "final",
    tipo: str = "solucao_final",
    prova: str | None = "E1-04",
    confirmacao: str | None = "E1-06",
    descartes: list[str] | None = None,
    obrigatorio: bool = True,
) -> ContratoEvidencia:
    return ContratoEvidencia(
        id=id_,
        conclusao="Conclusão fictícia comprovada por documentos independentes.",
        fase=fase,
        tipo=tipo,
        prova_principal=prova,
        confirmacao_independente=confirmacao,
        descarta_alternativas=descartes or [],
        personagens_afetados=["01"],
        acao_esperada_jogador="comparar documentos",
        risco_ambiguidade="baixo",
        obrigatoria_para_avanco=obrigatorio,
    )


def _blueprint_com_contratos(*contratos: ContratoEvidencia) -> Blueprint:
    blueprint = blueprint_valido()
    blueprint.contratos_evidencia = list(contratos)
    return blueprint


def _edge_relations(graph):
    return {(edge.source, edge.target, edge.relation) for edge in graph.edges}


def test_blueprint_sem_contratos_retorna_skipped_sem_orfaos_ruidosos():
    blueprint = blueprint_valido()
    graph = build_clue_graph(blueprint)

    report = analyze_clue_graph(graph, blueprint)

    assert graph.contracts == {}
    assert report["status"] == "skipped"
    assert report["summary"]["contracts"] == 0
    assert report["solution_paths"] == []
    assert report["cycles"] == []
    assert report["orphan_documents"] == []
    assert any(issue["code"] == "GP_006" and issue["severity"] == "warning" for issue in report["issues"])
    assert not any(issue["code"] == "GP_003" for issue in report["issues"])


def test_build_clue_graph_cria_nos_para_documentos_e_contratos():
    blueprint = _blueprint_com_contratos(_contrato())

    graph = build_clue_graph(blueprint)

    assert "E1-04" in graph.documents
    assert "C-FINAL-01" in graph.contracts
    assert any(node.id == "E1-04" and node.type == "document" for node in graph.nodes)
    assert any(node.id == "C-FINAL-01" and node.type == "contract" for node in graph.nodes)


def test_prova_principal_cria_aresta_documento_para_contrato():
    graph = build_clue_graph(_blueprint_com_contratos(_contrato()))

    assert ("E1-04", "C-FINAL-01", "proves") in _edge_relations(graph)


def test_confirmacao_independente_cria_aresta_documento_para_contrato():
    graph = build_clue_graph(_blueprint_com_contratos(_contrato()))

    assert ("E1-06", "C-FINAL-01", "confirms") in _edge_relations(graph)


def test_descarta_alternativas_cria_aresta_discards():
    graph = build_clue_graph(_blueprint_com_contratos(_contrato(descartes=["E1-05"])))

    assert ("E1-05", "C-FINAL-01", "discards") in _edge_relations(graph)


def test_graph_report_conta_documentos_contratos_nos_e_arestas():
    blueprint = _blueprint_com_contratos(_contrato(descartes=["E1-05"]))
    graph = build_clue_graph(blueprint)

    report = analyze_clue_graph(graph, blueprint)

    assert report["summary"]["documents"] == len(blueprint.documentos)
    assert report["summary"]["contracts"] == 1
    assert report["summary"]["nodes"] == len(blueprint.documentos) + 1
    assert report["summary"]["edges"] == 3


def test_documento_nao_usado_aparece_em_orphan_documents():
    blueprint = _blueprint_com_contratos(_contrato())
    blueprint.documentos.append(_documento("E2-99", Envelope.E2, TipoDocumento.PROTO))
    graph = build_clue_graph(blueprint)

    report = analyze_clue_graph(graph, blueprint)

    assert "E2-99" in report["orphan_documents"]
    assert any(issue["code"] == "GP_003" and issue["document"] == "E2-99" for issue in report["issues"])


def test_contrato_nao_obrigatorio_e_nao_final_aparece_em_orphan_contracts_e_dead_ends():
    contrato = _contrato("C-E1-ORFAO", fase="E1", tipo="oportunidade", obrigatorio=False)
    blueprint = _blueprint_com_contratos(contrato, _contrato())
    graph = build_clue_graph(blueprint)

    report = analyze_clue_graph(graph, blueprint)

    assert "C-E1-ORFAO" in report["orphan_contracts"]
    assert "C-E1-ORFAO" in report["dead_ends"]
    assert any(issue["code"] == "GP_004" and issue["contract"] == "C-E1-ORFAO" for issue in report["issues"])


def test_ausencia_de_contrato_final_gera_gp_006():
    blueprint = _blueprint_com_contratos(_contrato("C-E1-01", fase="E1", tipo="oportunidade"))
    graph = build_clue_graph(blueprint)

    report = analyze_clue_graph(graph, blueprint)

    assert report["status"] == "failed"
    assert any(issue["code"] == "GP_006" and issue["severity"] == "critical" for issue in report["issues"])


def test_contrato_final_valido_gera_solution_paths():
    blueprint = _blueprint_com_contratos(
        _contrato("C-E1-01", fase="E1", tipo="oportunidade", obrigatorio=True),
        _contrato("C-FINAL-01"),
    )
    graph = build_clue_graph(blueprint)

    report = analyze_clue_graph(graph, blueprint)

    assert report["solution_paths"] == [{
        "target": "C-FINAL-01",
        "depth": 2,
        "documents": ["E1-04", "E1-06"],
        "contracts": ["C-E1-01", "C-FINAL-01"],
    }]


def test_write_graph_report_escreve_json_valido(tmp_path: Path):
    blueprint = _blueprint_com_contratos(_contrato())
    report = analyze_clue_graph(build_clue_graph(blueprint), blueprint)

    path = write_graph_report(report, tmp_path / "graph_report.json")

    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8"))["summary"]["contracts"] == 1
