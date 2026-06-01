"""Feedback estruturado para correção futura de blueprints por LLM.

Este módulo não chama provedores de LLM. Ele apenas converte saídas técnicas do
validador, QA e grafo em instruções serializáveis para uso em ciclos futuros.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

Instruction = dict[str, str]

CATEGORY_UNKNOWN = "unknown"
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

CODE_MAPPING: dict[str, dict[str, str]] = {
    "CONT_001": {
        "category": "content_schema",
        "priority": PRIORITY_HIGH,
        "instruction": "Preencha o conteúdo do documento. Documento sem conteúdo não pode ser renderizado.",
        "reason": "Documentos sem conteúdo quebram a autossuficiência do dossiê e não geram material útil.",
        "suggested_action": "Preencher o conteúdo técnico do documento preservando sua função narrativa.",
    },
    "CONT_003": {
        "category": "content_schema",
        "priority": PRIORITY_HIGH,
        "instruction": "Preencha o campo obrigatório ausente no conteúdo do documento.",
        "reason": "Campos obrigatórios do template precisam existir para renderização e leitura corretas.",
        "suggested_action": "Adicionar o campo indicado com conteúdo específico, sem placeholder genérico.",
    },
    "CONT_REQUIRED_WHEN_001": {
        "category": "content_schema",
        "priority": PRIORITY_HIGH,
        "instruction": "A condição do template exige campos adicionais. Preencha os campos condicionais exigidos.",
        "reason": "Campos condicionais tornam o documento coerente com a variação de template escolhida.",
        "suggested_action": "Identificar a condição ativada e preencher todos os campos dependentes no conteúdo.",
    },
    "CONT_ITEM_001": {
        "category": "content_schema",
        "priority": PRIORITY_HIGH,
        "instruction": "Corrija os itens da lista do documento, preenchendo os campos obrigatórios de cada item.",
        "reason": "Listas incompletas geram tabelas ou blocos narrativos quebrados.",
        "suggested_action": "Revisar cada item da lista e preencher os campos obrigatórios faltantes.",
    },
    "DOC_008": {
        "category": "document_structure",
        "priority": PRIORITY_HIGH,
        "instruction": "Corrija códigos duplicados de documentos. Cada documento precisa ter código único.",
        "reason": "Códigos duplicados impedem referência inequívoca entre pistas, contratos e manifest.",
        "suggested_action": "Renomear documentos duplicados e atualizar todas as referências afetadas.",
    },
    "ENV_001": {
        "category": "envelope_structure",
        "priority": PRIORITY_HIGH,
        "instruction": "Corrija o envelope para o padrão E1, E2, E3...",
        "reason": "Envelopes fora do padrão quebram a progressão e o empacotamento final.",
        "suggested_action": "Ajustar o valor do envelope para um identificador sequencial válido.",
    },
    "ENV_003": {
        "category": "envelope_structure",
        "priority": PRIORITY_HIGH,
        "instruction": "Corrija a sequência de envelopes. Não pode haver buracos como E1 e E3 sem E2.",
        "reason": "A progressão dos envelopes precisa ser contínua para evitar saltos investigativos.",
        "suggested_action": "Adicionar documentos no envelope ausente ou renumerar envelopes mantendo a ordem narrativa.",
    },
    "ENV_004": {
        "category": "envelope_structure",
        "priority": PRIORITY_HIGH,
        "instruction": "O blueprint declara mais envelopes do que realmente usa. Ajuste formato_envelopes ou adicione documentos no envelope declarado.",
        "reason": "A declaração de formato precisa refletir o pacote que será produzido.",
        "suggested_action": "Reduzir formato_envelopes ou distribuir documentos no envelope declarado sem violar a progressão.",
    },
    "ENV_005": {
        "category": "envelope_structure",
        "priority": PRIORITY_HIGH,
        "instruction": "O blueprint usa envelopes acima do declarado. Ajuste formato_envelopes para refletir o maior envelope real ou remova os documentos excedentes.",
        "reason": "Documentos em envelopes não declarados podem ficar fora do pacote ou romper a sequência.",
        "suggested_action": "Atualizar formato_envelopes ou mover/remover documentos do envelope excedente.",
    },
    "CE_003": {
        "category": "evidence_contract",
        "priority": PRIORITY_HIGH,
        "instruction": "Referencie uma prova_principal existente no blueprint.",
        "reason": "Todo contrato precisa apontar para uma evidência real do dossiê.",
        "suggested_action": "Corrigir o código da prova_principal ou criar o documento correspondente.",
    },
    "CE_004": {
        "category": "evidence_contract",
        "priority": PRIORITY_HIGH,
        "instruction": "Referencie uma confirmacao_independente existente no blueprint.",
        "reason": "Confirmação independente só é válida quando aponta para documento existente.",
        "suggested_action": "Corrigir o código da confirmacao_independente ou criar um documento de confirmação.",
    },
    "CE_005": {
        "category": "evidence_contract",
        "priority": PRIORITY_HIGH,
        "instruction": "Use documentos diferentes para prova principal e confirmação independente.",
        "reason": "A mesma evidência não pode servir como prova principal e confirmação independente.",
        "suggested_action": "Adicionar ou referenciar outro documento que confirme a mesma conclusão por caminho independente.",
    },
    "CE_006": {
        "category": "evidence_contract",
        "priority": PRIORITY_HIGH,
        "instruction": "Corrija descarta_alternativas para referenciar apenas documentos existentes.",
        "reason": "Alternativas só podem ser descartadas por evidências presentes no blueprint.",
        "suggested_action": "Remover referências inexistentes ou criar os documentos de descarte necessários.",
    },
    "CE_007": {
        "category": "evidence_contract",
        "priority": PRIORITY_HIGH,
        "instruction": "Contrato de fase anterior não pode depender de documento de envelope posterior.",
        "reason": "E1 não pode depender de E2; a solução de cada fase deve ser possível com documentos já liberados.",
        "suggested_action": "Mover a evidência para envelope anterior ou alterar o contrato para uma fase compatível.",
    },
    "CE_008": {
        "category": "evidence_contract",
        "priority": PRIORITY_HIGH,
        "instruction": "Contrato obrigatório precisa ter prova principal e confirmação independente.",
        "reason": "Contratos obrigatórios sem dupla sustentação tornam o avanço ambíguo ou chutável.",
        "suggested_action": "Preencher prova_principal e confirmacao_independente com documentos distintos e existentes.",
    },
    "CE_009": {
        "category": "evidence_contract",
        "priority": PRIORITY_MEDIUM,
        "instruction": "Reduza ambiguidade do contrato obrigatório ou adicione confirmação mais forte.",
        "reason": "Contratos obrigatórios com alto risco de ambiguidade enfraquecem a solvabilidade.",
        "suggested_action": "Reescrever a conclusão ou reforçar a confirmação independente.",
    },
    "CE_010": {
        "category": "evidence_contract",
        "priority": PRIORITY_MEDIUM,
        "instruction": "Defina a ação esperada do jogador para resolver essa conclusão.",
        "reason": "A ação esperada orienta como o contrato será validado durante a investigação.",
        "suggested_action": "Adicionar uma ação observável e concreta que conecte documentos à conclusão.",
    },
    "GP_003": {
        "category": "clue_graph",
        "priority": PRIORITY_MEDIUM,
        "instruction": "Revise o documento órfão. Conecte-o a algum contrato de evidência ou marque sua função narrativa.",
        "reason": "Documentos órfãos podem indicar pista sem função ou material que não participa da solução.",
        "suggested_action": "Referenciar o documento em um contrato ou justificar sua função como suporte/red herring.",
    },
    "GP_004": {
        "category": "clue_graph",
        "priority": PRIORITY_MEDIUM,
        "instruction": "Revise o contrato órfão. Conecte-o a uma conclusão maior ou torne-o obrigatório/final se for relevante.",
        "reason": "Contratos sem papel na progressão podem virar becos sem saída lógicos.",
        "suggested_action": "Marcar o contrato como obrigatório/final ou conectar sua conclusão ao caminho principal.",
    },
    "GP_006": {
        "category": "clue_graph",
        "priority": PRIORITY_MEDIUM,
        "instruction": "Adicione contrato de solução final ou aceite que o grafo está incompleto em blueprint legado.",
        "reason": "Sem contrato final, o grafo não consegue demonstrar o fechamento da solução.",
        "suggested_action": "Criar um contrato final que conecte documentos, confirmações e conclusões dos envelopes.",
    },
    "GP_007": {
        "category": "clue_graph",
        "priority": PRIORITY_HIGH,
        "instruction": "Contrato final precisa de caminho documental mínimo com prova e confirmação independentes.",
        "reason": "A solução final precisa ser sustentada por evidências independentes.",
        "suggested_action": "Definir prova_principal e confirmacao_independente distintas para o contrato final.",
    },
    "QA_FILE_001": {
        "category": "qa_package",
        "priority": PRIORITY_HIGH,
        "instruction": "Arquivo listado no manifest não existe. Corrija geração/manifest.",
        "reason": "O pacote final não pode apontar para arquivos ausentes.",
        "suggested_action": "Garantir que o arquivo seja gerado ou remover a entrada incorreta do manifest.",
    },
    "QA_FILE_002": {
        "category": "qa_package",
        "priority": PRIORITY_HIGH,
        "instruction": "PDF inválido ou vazio. Corrija renderização.",
        "reason": "PDFs vazios ou ilegíveis impedem a entrega do pacote final.",
        "suggested_action": "Revisar a renderização do documento e gerar novamente o PDF válido.",
    },
    "QA_DOC_004": {
        "category": "qa_package",
        "priority": PRIORITY_HIGH,
        "instruction": "Documento duplicado no manifest. Garanta códigos únicos e mapeamento correto.",
        "reason": "Duplicidade no manifest torna páginas e referências ambíguas.",
        "suggested_action": "Corrigir códigos e reconstruir o manifest sem duplicatas.",
    },
}

CONTRACT_RE = re.compile(r"\bC-[A-Z0-9][A-Z0-9_-]*(?:-[A-Z0-9][A-Z0-9_-]*)*\b")
DOCUMENT_RE = re.compile(r"\bE[1-9]\d*-\d{2,}\b")


def _to_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if is_dataclass(value):
        return asdict(value)
    data: dict[str, Any] = {}
    for name in ["codigo", "code", "severidade", "severity", "mensagem", "message", "detalhe", "detail", "documento", "document", "file", "contract"]:
        if hasattr(value, name):
            data[name] = getattr(value, name)
    return data


def _text(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _severity(value: Any) -> str:
    normalized = _text(value).strip().lower()
    return normalized.replace("í", "i").replace("é", "e").replace("á", "a")


def _fallback_priority(severity: Any) -> str:
    normalized = _severity(severity)
    if normalized in {"critico", "critical", "error", "erro", "high"}:
        return PRIORITY_HIGH
    if normalized in {"moderado", "warning", "warn", "medium", "skipped"}:
        return PRIORITY_MEDIUM
    return PRIORITY_LOW


def _mapping_for(code: str, severity: Any) -> dict[str, str]:
    base = dict(CODE_MAPPING.get(code, {}))
    if code == "GP_006":
        base["priority"] = PRIORITY_HIGH if _fallback_priority(severity) == PRIORITY_HIGH else PRIORITY_MEDIUM
    return base


def _target_from_text(*texts: str) -> str | None:
    for text in texts:
        match = re.search(r"Contrato:\s*([A-Za-z0-9_-]+(?:-[A-Za-z0-9_-]+)*)", text)
        if match:
            return match.group(1).rstrip(".,;:")
    joined = " ".join(texts)
    contract = CONTRACT_RE.search(joined)
    if contract:
        return contract.group(0).rstrip(".,;:")
    document = DOCUMENT_RE.search(joined)
    if document:
        return document.group(0).rstrip(".,;:")
    return None


def _base_instruction(data: dict[str, Any], source: str, default_target: str) -> Instruction:
    code = _text(data.get("codigo") or data.get("code") or "UNKNOWN") or "UNKNOWN"
    severity = data.get("severidade") or data.get("severity")
    message = _text(data.get("mensagem") or data.get("message") or "Item técnico requer revisão.")
    detail = _text(data.get("detalhe") or data.get("detail"))
    mapped = _mapping_for(code, severity)
    return {
        "code": code,
        "priority": mapped.get("priority") or _fallback_priority(severity),
        "target": default_target,
        "category": mapped.get("category", CATEGORY_UNKNOWN),
        "instruction": mapped.get("instruction", message),
        "reason": mapped.get("reason", detail or message),
        "suggested_action": mapped.get(
            "suggested_action",
            "Revise o item apontado e corrija o blueprint preservando a intenção narrativa.",
        ),
        "source": source,
    }


def instruction_from_validation_error(error: Any) -> Instruction:
    """Converte um erro/aviso do validator em instrução para correção futura."""
    data = _to_mapping(error)
    message = _text(data.get("mensagem") or data.get("message"))
    detail = _text(data.get("detalhe") or data.get("detail"))
    target = _text(data.get("documento") or data.get("document")) or _target_from_text(detail, message) or "Blueprint"
    return _base_instruction(data, "validator", target)


def instruction_from_qa_issue(issue: Any) -> Instruction:
    """Converte um erro/aviso do QA em instrução para correção futura."""
    data = _to_mapping(issue)
    target = _text(data.get("file")) or _text(data.get("document")) or "Package"
    return _base_instruction(data, "qa", target)


def instruction_from_graph_issue(issue: Any) -> Instruction:
    """Converte uma issue do graph_report em instrução para correção futura."""
    data = _to_mapping(issue)
    target = _text(data.get("contract")) or _text(data.get("document")) or "Graph"
    return _base_instruction(data, "graph", target)


def _validation_items(validation_result: Any) -> tuple[list[Any], list[Any], list[Any]]:
    criticos = list(getattr(validation_result, "criticos", []))
    erros = list(getattr(validation_result, "erros", []))
    avisos = list(getattr(validation_result, "avisos", []))
    non_critical_errors = [erro for erro in erros if erro not in criticos]
    return criticos, non_critical_errors, avisos


def _qa_issues(qa_report: dict[str, Any] | None) -> tuple[list[Any], list[Any]]:
    if not qa_report:
        return [], []
    return list(qa_report.get("errors", [])), list(qa_report.get("warnings", []))


def _graph_issues(graph_report: dict[str, Any] | None) -> tuple[list[Any], list[Any]]:
    if not graph_report:
        return [], []
    critical: list[Any] = []
    warnings: list[Any] = []
    for issue in graph_report.get("issues", []):
        severity = _severity(_to_mapping(issue).get("severity"))
        if severity in {"critical", "critico", "error", "erro"}:
            critical.append(issue)
        else:
            warnings.append(issue)
    return critical, warnings


def build_llm_feedback(
    validation_result: Any,
    qa_report: dict[str, Any] | None = None,
    graph_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Monta feedback estruturado serializável para JSON.

    A saída é um artefato técnico. Ela não executa correção, não chama LLM e não
    altera o blueprint original.
    """
    criticos, non_critical_errors, validation_warnings = _validation_items(validation_result)
    qa_errors, qa_warnings = _qa_issues(qa_report)
    graph_critical, graph_warnings = _graph_issues(graph_report)

    instructions: list[Instruction] = []
    instructions.extend(instruction_from_validation_error(error) for error in criticos)
    instructions.extend(instruction_from_validation_error(error) for error in non_critical_errors)
    instructions.extend(instruction_from_validation_error(error) for error in validation_warnings)
    instructions.extend(instruction_from_qa_issue(issue) for issue in qa_errors)
    instructions.extend(instruction_from_qa_issue(issue) for issue in qa_warnings)
    instructions.extend(instruction_from_graph_issue(issue) for issue in graph_critical)
    instructions.extend(instruction_from_graph_issue(issue) for issue in graph_warnings)

    critical_count = len(criticos) + len(qa_errors) + len(graph_critical)
    warning_count = len(non_critical_errors) + len(validation_warnings) + len(qa_warnings) + len(graph_warnings)
    status = "passed" if critical_count == 0 else "needs_revision"
    summary = (
        "Blueprint validado sem bloqueios críticos."
        if status == "passed"
        else "Blueprint precisa de revisão antes de gerar pacote final."
    )
    return {
        "status": status,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "summary": summary,
        "instructions": instructions,
    }


def write_llm_feedback(feedback: dict[str, Any], output_path: Path) -> Path:
    """Escreve feedback estruturado em JSON UTF-8."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(feedback, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
