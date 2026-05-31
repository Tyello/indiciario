"""Grafo lógico de pistas e contratos de evidência.

Este módulo não cria visualizações. Ele transforma um ``Blueprint`` em uma
representação simples e serializável para medir solvabilidade estrutural.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

try:  # Execução como pacote
    from .models import Blueprint, ContratoEvidencia, Documento
except ImportError:  # Execução direta a partir de generator/
    from models import Blueprint, ContratoEvidencia, Documento  # type: ignore[no-redef]

NodeType = Literal["document", "contract"]


@dataclass(frozen=True)
class GraphNode:
    """Nó lógico do grafo de pistas."""

    id: str
    type: NodeType
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class GraphEdge:
    """Aresta direcionada entre documento e contrato."""

    source: str
    target: str
    relation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
        }


@dataclass
class ClueGraph:
    """Grafo lógico construído a partir do blueprint."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
    documents: dict[str, Documento]
    contracts: dict[str, ContratoEvidencia]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "documents": sorted(self.documents),
            "contracts": sorted(self.contracts),
        }


def _is_final_contract(contrato: ContratoEvidencia) -> bool:
    return contrato.fase == "final" or contrato.tipo == "solucao_final"


def _issue(
    code: str,
    severity: str,
    message: str,
    *,
    document: str | None = None,
    contract: str | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "message": message,
    }
    if document is not None:
        data["document"] = document
    if contract is not None:
        data["contract"] = contract
    return data


def build_clue_graph(blueprint: Blueprint) -> ClueGraph:
    """Constrói o grafo lógico documento -> contrato a partir do blueprint."""
    documents = {doc.codigo: doc for doc in blueprint.documentos}
    contracts = {contrato.id: contrato for contrato in blueprint.contratos_evidencia}
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    for doc in blueprint.documentos:
        nodes.append(GraphNode(
            id=doc.codigo,
            type="document",
            label=doc.titulo,
            metadata={
                "envelope": doc.envelope,
                "tipo": doc.tipo.value,
            },
        ))

    for contrato in blueprint.contratos_evidencia:
        nodes.append(GraphNode(
            id=contrato.id,
            type="contract",
            label=contrato.conclusao or contrato.id,
            metadata={
                "fase": contrato.fase,
                "tipo": contrato.tipo,
                "conclusao": contrato.conclusao,
                "obrigatoria_para_avanco": contrato.obrigatoria_para_avanco,
                "risco_ambiguidade": contrato.risco_ambiguidade,
            },
        ))
        if contrato.prova_principal in documents:
            edges.append(GraphEdge(contrato.prova_principal or "", contrato.id, "proves"))
        if contrato.confirmacao_independente in documents:
            edges.append(GraphEdge(contrato.confirmacao_independente or "", contrato.id, "confirms"))
        for doc_codigo in contrato.descarta_alternativas:
            if doc_codigo in documents:
                edges.append(GraphEdge(doc_codigo, contrato.id, "discards"))

    return ClueGraph(nodes=nodes, edges=edges, documents=documents, contracts=contracts)


def _used_documents(graph: ClueGraph) -> set[str]:
    return {edge.source for edge in graph.edges if edge.source in graph.documents}


def _solution_path(target: ContratoEvidencia, graph: ClueGraph) -> dict[str, Any]:
    target_docs = [
        codigo
        for codigo in [target.prova_principal, target.confirmacao_independente, *target.descarta_alternativas]
        if codigo and codigo in graph.documents
    ]
    contracts = [
        contrato.id
        for contrato in graph.contracts.values()
        if contrato.obrigatoria_para_avanco and contrato.id != target.id and not _is_final_contract(contrato)
    ]
    contracts.append(target.id)
    return {
        "target": target.id,
        "depth": len(contracts),
        "documents": sorted(set(target_docs)),
        "contracts": contracts,
    }


def analyze_clue_graph(graph: ClueGraph, blueprint: Blueprint) -> dict[str, Any]:
    """Gera relatório de solvabilidade estrutural em tipos JSON puros."""
    del blueprint
    issues: list[dict[str, Any]] = []

    for contrato in graph.contracts.values():
        if not contrato.prova_principal:
            issues.append(_issue(
                "GP_001",
                "critical",
                f"Contrato '{contrato.id}' não define prova_principal.",
                contract=contrato.id,
            ))
        if not contrato.conclusao.strip():
            issues.append(_issue(
                "GP_002",
                "critical",
                f"Contrato '{contrato.id}' não define conclusão.",
                contract=contrato.id,
            ))

    used_docs = _used_documents(graph)
    orphan_documents = sorted(set(graph.documents) - used_docs)
    for doc_codigo in orphan_documents:
        issues.append(_issue(
            "GP_003",
            "warning",
            f"Documento '{doc_codigo}' não participa de nenhum contrato de evidência.",
            document=doc_codigo,
        ))

    final_contracts = [contrato for contrato in graph.contracts.values() if _is_final_contract(contrato)]
    orphan_contracts = sorted(
        contrato.id
        for contrato in graph.contracts.values()
        if not contrato.obrigatoria_para_avanco and not _is_final_contract(contrato)
    )
    dead_ends = list(orphan_contracts)
    for contrato_id in orphan_contracts:
        issues.append(_issue(
            "GP_004",
            "warning",
            f"Contrato '{contrato_id}' não é obrigatório nem final; pode ser beco sem saída lógico.",
            contract=contrato_id,
        ))

    if not final_contracts:
        issues.append(_issue(
            "GP_006",
            "critical",
            "Nenhum contrato de solução final encontrado.",
        ))

    for contrato in final_contracts:
        prova = contrato.prova_principal
        confirmacao = contrato.confirmacao_independente
        if (
            not prova
            or not confirmacao
            or prova == confirmacao
            or prova not in graph.documents
            or confirmacao not in graph.documents
        ):
            issues.append(_issue(
                "GP_007",
                "critical",
                f"Contrato final '{contrato.id}' não tem caminho documental mínimo válido.",
                contract=contrato.id,
            ))

    solution_paths = [_solution_path(contrato, graph) for contrato in final_contracts]
    status = "failed" if any(issue["severity"] == "critical" for issue in issues) else "passed"
    return {
        "status": status,
        "summary": {
            "documents": len(graph.documents),
            "contracts": len(graph.contracts),
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
            "solution_targets": len(final_contracts),
        },
        "orphan_documents": orphan_documents,
        "orphan_contracts": orphan_contracts,
        "dead_ends": dead_ends,
        "cycles": [],
        "solution_paths": solution_paths,
        "issues": issues,
    }


def write_graph_report(report: dict[str, Any], output_path: Path) -> Path:
    """Escreve ``graph_report.json`` em disco."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
