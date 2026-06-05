"""Guardrail anti-obviedade para documentos de jogador.

O checker usa heurísticas conservadoras: ele procura padrões que costumam
entregar solução em documentos diegéticos, mas evita bloquear ambiguidade boa.
O objetivo é levantar achados acionáveis para o validator, não substituir a
revisão editorial humana.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


class ObviousnessSeverity(str, Enum):
    CRITICAL = "critical"
    MODERATE = "moderate"
    WARNING = "warning"


@dataclass(frozen=True)
class ObviousnessFinding:
    code: str
    severity: ObviousnessSeverity
    message: str
    document: str | None = None
    detail: str | None = None
    path: str | None = None


@dataclass
class ObviousnessReport:
    findings: list[ObviousnessFinding] = field(default_factory=list)

    @property
    def critical(self) -> list[ObviousnessFinding]:
        return [finding for finding in self.findings if finding.severity == ObviousnessSeverity.CRITICAL]

    @property
    def moderate(self) -> list[ObviousnessFinding]:
        return [finding for finding in self.findings if finding.severity == ObviousnessSeverity.MODERATE]

    @property
    def warnings(self) -> list[ObviousnessFinding]:
        return [finding for finding in self.findings if finding.severity == ObviousnessSeverity.WARNING]

    @property
    def has_blocking_findings(self) -> bool:
        return bool(self.critical or self.moderate)

    def add(
        self,
        code: str,
        severity: ObviousnessSeverity,
        message: str,
        *,
        document: str | None = None,
        detail: str | None = None,
        path: str | None = None,
    ) -> None:
        finding = ObviousnessFinding(code, severity, message, document, detail, path)
        if finding not in self.findings:
            self.findings.append(finding)


_PLAYER_DOCUMENT_TYPES = {
    "auditoria",
    "boletim",
    "cadastro_terceiros",
    "cartao",
    "carta",
    "chat",
    "contrato",
    "depoimento",
    "email_institucional",
    "email_narrador",
    "escala",
    "extrato",
    "folha_cruzamento",
    "glossario",
    "linha_tempo_fechamento",
    "log_acesso",
    "log_sistema",
    "manual",
    "mapa",
    "orcamento",
    "outro",
    "protocolo",
    "recibo",
}

_OPERATIONAL_TYPES = {"log_acesso", "log_sistema", "escala"}
_HIGHER_THAN_BEGINNER = {"intermediario", "avancado", "especialista", "mestre", "medio", "medio_alto", "dificil"}
_INTERNAL_FIELD_NAMES = {
    "verdade_real",
    "observacoes_producao",
    "gabarito",
    "cadeia_causal",
    "metodo_ocultacao",
}

_CONCLUSIVE_PATTERNS = [
    r"\bclaramente\s+foi\b",
    r"\bevidentemente\b",
    r"\be\s+(?:o\s+|a\s+)?culpad[oa]\b",
    r"\bfoi\s+provad[oa]\b",
    r"\bsem\s+duvida\s+alguma\b",
    r"\bconfessou\b",
    r"\be\s+(?:o\s+|a\s+)?responsavel\s+(?:pelo|pela)\s+(?:crime|desvio|troca|morte|sabotagem)\b",
    r"\bplanejou\s+o\s+crime\b",
    r"\bcometeu\s+o\s+crime\b",
]

_AUTHORIAL_PATTERNS = [
    r"\bcompare\s+(?:com|este|esta)\b",
    r"\bcruze\s+com\b",
    r"\bnao\s+prova\s+sozinh[oa]\b",
    r"\bnao\s+decide\s+isoladamente\b",
    r"\ba\s+solucao\s+depende\s+de\b",
    r"\bred\s*herring\b",
    r"\brui?do\s+controlado\b",
    r"\bgabarito\b",
]

_CONFESSION_PATTERNS = [
    r"\b(?:eu|nos)\s+(?:fiz|fizemos|planejei|planejamos|armei|armamos|sabotei|sabotamos|adulterei|adulteramos|troquei|trocamos|envenenei|envenenamos|matei|matamos|roubei|roubamos|desviei|desviamos)\b",
    r"\bfui\s+eu\s+que\b",
    r"\bfomos\s+nos\s+que\b",
]

_INCRIMINATING_VERBS = {
    "adulterou",
    "adulterar",
    "alterou",
    "alterar",
    "apagou",
    "apagar",
    "armou",
    "armar",
    "confessou",
    "desviou",
    "desviar",
    "envenenou",
    "envenenar",
    "escondeu",
    "esconder",
    "falsificou",
    "falsificar",
    "forjou",
    "forjar",
    "impedir",
    "impediu",
    "incriminou",
    "incriminar",
    "matou",
    "matar",
    "planejou",
    "planejar",
    "retirou",
    "retirar",
    "roubou",
    "roubar",
    "sabotar",
    "sabotou",
    "sumiu",
    "sumir",
    "tirou",
    "trocar",
    "trocou",
}

_CRITICAL_CONTEXT = {
    "álibi",
    "alibi",
    "autoria",
    "brinde",
    "cálice",
    "calice",
    "carga",
    "chave",
    "crime",
    "culpa",
    "culpado",
    "desvio",
    "elevador",
    "envenenamento",
    "galeria",
    "herança",
    "heranca",
    "morte",
    "peça",
    "peca",
    "plano",
    "prova",
    "reserva",
    "rouparia",
    "salao",
    "salão",
    "taça",
    "taca",
    "vitrine",
}

_SOLVES_WHO = {"culpado", "culpada", "autor", "autora", "responsável", "responsavel", "quem fez"}
_SOLVES_HOW = {"como fez", "método", "metodo", "modus", "veneno", "adulteração", "adulteracao", "troca"}
_SOLVES_WHY = {"motivo", "motivação", "motivacao", "vingança", "vinganca", "benefício", "beneficio"}


def check_obviousness(blueprint: dict[str, Any]) -> ObviousnessReport:
    """Verifica se documentos de jogador entregam a solução cedo demais."""
    report = ObviousnessReport()
    difficulty = _norm(str(blueprint.get("dificuldade", "")))
    culprit_names = _culprit_names(blueprint)
    internal_fragments = _internal_value_fragments(blueprint)
    documents = blueprint.get("documentos", [])
    if not isinstance(documents, list):
        return report

    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            continue
        doc_type = str(document.get("tipo", ""))
        if doc_type not in _PLAYER_DOCUMENT_TYPES:
            continue
        code = str(document.get("codigo", f"documentos[{index}]"))
        envelope = str(document.get("envelope", ""))
        content_items = list(_iter_text(document.get("conteudo", {}), f"documentos[{index}].conteudo"))
        content_text = "\n".join(text for _, text in content_items)
        content_norm = _norm(content_text)
        objective = str(document.get("objetivo_narrativo", ""))
        objective_norm = _norm(objective)
        emotion_norm = _norm(str(document.get("emocao_esperada", "")))

        _check_internal_leaks(report, code, content_items, internal_fragments)
        _check_confessions(report, code, content_norm, doc_type)
        _check_conclusive_language(report, code, content_norm)
        _check_authorial_language(report, code, content_norm)
        _check_document_codes_in_content(report, code, content_text)
        _check_culprit_action_context(report, code, content_norm, culprit_names)
        _check_objective_culprit_action(report, code, objective_norm, culprit_names)
        _check_e1_anticipation(report, code, envelope, objective_norm, emotion_norm, content_norm, culprit_names)
        _check_chat(report, code, doc_type, content_norm, culprit_names)
        _check_deposition(report, code, doc_type, content_norm, culprit_names)
        _check_single_document_solution(report, code, content_norm)
        _check_operational_names(report, code, doc_type, difficulty, content_items, culprit_names)

    return report


def _culprit_names(blueprint: dict[str, Any]) -> set[str]:
    culprit_ids = {
        str(blueprint.get("executor_id", "")),
        str(blueprint.get("planejador_id", "")),
        str(blueprint.get("beneficiario_id", "")),
    }
    names: set[str] = set()
    for character in blueprint.get("personagens", []):
        if not isinstance(character, dict) or str(character.get("id", "")) not in culprit_ids:
            continue
        raw_name = str(character.get("nome", "")).strip()
        if not raw_name:
            continue
        normalized = _norm(raw_name)
        names.add(normalized)
        first = normalized.split()[0]
        if len(first) >= 4:
            names.add(first)
    return names


def _internal_value_fragments(blueprint: dict[str, Any]) -> list[tuple[str, str]]:
    fragments: list[tuple[str, str]] = []
    for field_name in ["verdade_real", "metodo_ocultacao", "observacoes_producao"]:
        value = blueprint.get(field_name)
        fragments.extend((f"{field_name}: {fragment}", fragment) for fragment in _relevant_fragments(value))

    causal_chain = blueprint.get("cadeia_causal", [])
    if isinstance(causal_chain, list):
        for index, item in enumerate(causal_chain):
            fragments.extend((f"cadeia_causal[{index}]: {fragment}", fragment) for fragment in _relevant_fragments(item))

    unique: list[tuple[str, str]] = []
    seen: set[str] = set()
    for source, fragment in fragments:
        if fragment not in seen:
            unique.append((source, fragment))
            seen.add(fragment)
    return unique


def _relevant_fragments(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    normalized = _norm(value)
    if len(normalized) < 40:
        return []

    fragments: list[str] = []
    if len(normalized) <= 220:
        fragments.append(normalized)

    for sentence in _sentences(normalized):
        if len(sentence) >= 50:
            fragments.append(sentence)

    for separator in [";", " — ", " - "]:
        for part in normalized.split(separator):
            part = part.strip()
            if len(part) >= 60:
                fragments.append(part)

    return fragments


def _check_internal_leaks(
    report: ObviousnessReport,
    code: str,
    items: list[tuple[str, str]],
    internal_fragments: list[tuple[str, str]],
) -> None:
    for path, text in items:
        normalized = _norm(text)
        for field_name in _INTERNAL_FIELD_NAMES:
            if field_name in normalized:
                report.add(
                    "OBV_010",
                    ObviousnessSeverity.CRITICAL,
                    "Campo interno parece ter vazado para conteúdo de documento do jogador.",
                    document=code,
                    detail=field_name,
                    path=path,
                )
        for source, fragment in internal_fragments:
            if fragment in normalized:
                report.add(
                    "OBV_010",
                    ObviousnessSeverity.CRITICAL,
                    "Valor interno do blueprint parece ter vazado para conteúdo de documento do jogador.",
                    document=code,
                    detail=source,
                    path=path,
                )


def _check_confessions(report: ObviousnessReport, code: str, text: str, doc_type: str) -> None:
    for pattern in _CONFESSION_PATTERNS:
        if re.search(pattern, text):
            report.add(
                "OBV_003",
                ObviousnessSeverity.CRITICAL,
                "Confissão em primeira pessoa detectada em documento do jogador.",
                document=code,
                detail="Chats, e-mails e depoimentos não devem dizer 'eu fiz' ou equivalente.",
            )
            if doc_type == "chat":
                report.add(
                    "OBV_007",
                    ObviousnessSeverity.CRITICAL,
                    "Chat contém linguagem confessional em vez de exportação operacional ambígua.",
                    document=code,
                )
            return


def _check_conclusive_language(report: ObviousnessReport, code: str, text: str) -> None:
    for pattern in _CONCLUSIVE_PATTERNS:
        if re.search(pattern, text):
            report.add(
                "OBV_006",
                ObviousnessSeverity.MODERATE,
                "Linguagem conclusiva detectada em documento do jogador.",
                document=code,
                detail=pattern,
            )
            return


def _check_authorial_language(report: ObviousnessReport, code: str, text: str) -> None:
    for pattern in _AUTHORIAL_PATTERNS:
        if re.search(pattern, text):
            report.add(
                "OBV_012",
                ObviousnessSeverity.MODERATE,
                "Linguagem de autor/facilitador detectada em conteúdo diegético.",
                document=code,
                detail=pattern,
            )
            return


def _check_document_codes_in_content(report: ObviousnessReport, code: str, text: str) -> None:
    normalized = _norm(text)
    has_instructional_cross_ref = re.search(r"\b(?:compare|cruze|confira|confronte|verifique)\b", normalized)
    matches = sorted(set(re.findall(r"\bE[1-9]\d*-\d{2,}\b", text)))
    cross_refs = [match for match in matches if match != code]
    if cross_refs and has_instructional_cross_ref:
        report.add(
            "OBV_011",
            ObviousnessSeverity.WARNING,
            "Referência instrucional a código de documento encontrada dentro de conteúdo diegético.",
            document=code,
            detail=", ".join(cross_refs[:5]),
        )


def _check_culprit_action_context(report: ObviousnessReport, code: str, text: str, names: set[str]) -> None:
    for sentence in _sentences(text):
        if not _contains_any_name(sentence, names):
            continue
        if _contains_token(sentence, _INCRIMINATING_VERBS) and _contains_token(sentence, _CRITICAL_CONTEXT):
            report.add(
                "OBV_002",
                ObviousnessSeverity.MODERATE,
                "Nome de culpado aparece junto de verbo incriminador e contexto crítico no mesmo trecho.",
                document=code,
                detail=_clip(sentence),
            )
            return


def _check_objective_culprit_action(report: ObviousnessReport, code: str, objective: str, names: set[str]) -> None:
    if _contains_any_name(objective, names) and _contains_token(objective, _INCRIMINATING_VERBS):
        report.add(
            "OBV_004",
            ObviousnessSeverity.WARNING,
            "objetivo_narrativo nomeia culpado junto de ação potencialmente incriminadora.",
            document=code,
            detail="Campo interno permitido, mas pode contaminar o tom do documento.",
        )


def _check_e1_anticipation(
    report: ObviousnessReport,
    code: str,
    envelope: str,
    objective: str,
    emotion: str,
    content: str,
    names: set[str],
) -> None:
    if envelope != "E1":
        return
    player_facing = f"{emotion}\n{content}"
    combined = f"{objective}\n{player_facing}"
    has_solution_word = any(term in player_facing for term in ["solucao final", "solução final", "gabarito", "culpado revelado", "confissao", "confissão"])
    has_culprit_conclusion = _contains_any_name(combined, names) and any(
        term in player_facing for term in ["culpado", "culpada", "quem fez", "autor do crime", "autora do crime"]
    )
    if has_solution_word or has_culprit_conclusion:
        report.add(
            "OBV_005",
            ObviousnessSeverity.MODERATE,
            "Envelope 1 antecipa solução, gabarito, confissão ou culpado revelado.",
            document=code,
        )


def _check_chat(report: ObviousnessReport, code: str, doc_type: str, text: str, names: set[str]) -> None:
    if doc_type != "chat":
        return
    direct_crime = any(term in text for term in ["foi voce que", "foi você que", "o plano deu certo", "ninguém vai descobrir", "ninguem vai descobrir"])
    culprit_incriminating = any(
        _contains_any_name(sentence, names) and _contains_token(sentence, _INCRIMINATING_VERBS) and _contains_token(sentence, _CRITICAL_CONTEXT)
        for sentence in _sentences(text)
    )
    if direct_crime or culprit_incriminating:
        report.add(
            "OBV_007",
            ObviousnessSeverity.CRITICAL,
            "Chat explica o crime diretamente; chats devem ser operacionais e ambíguos.",
            document=code,
        )


def _check_deposition(report: ObviousnessReport, code: str, doc_type: str, text: str, names: set[str]) -> None:
    if doc_type != "depoimento":
        return
    for sentence in _sentences(text):
        if not _contains_any_name(sentence, names):
            continue
        if re.search(r"\b(?:planejou|pretendia|queria|tinha\s+a\s+intencao|foi\s+(?:o|a)\s+responsavel|e\s+(?:o|a)\s+culpad[oa])\b", sentence):
            report.add(
                "OBV_008",
                ObviousnessSeverity.MODERATE,
                "Depoimento afirma autoria, intenção ou plano de terceiro como fato estabelecido.",
                document=code,
                detail=_clip(sentence),
            )
            return


def _check_single_document_solution(report: ObviousnessReport, code: str, text: str) -> None:
    solves_who = _contains_token(text, _SOLVES_WHO)
    solves_how = _contains_token(text, _SOLVES_HOW)
    solves_why = _contains_token(text, _SOLVES_WHY)
    benefit = "beneficio" in text or "benefício" in text or "vantagem" in text
    if solves_who and solves_how and solves_why and benefit:
        report.add(
            "OBV_009",
            ObviousnessSeverity.MODERATE,
            "Documento parece responder sozinho quem, como, por quê e benefício.",
            document=code,
        )


def _check_operational_names(
    report: ObviousnessReport,
    code: str,
    doc_type: str,
    difficulty: str,
    items: list[tuple[str, str]],
    names: set[str],
) -> None:
    if doc_type not in _OPERATIONAL_TYPES or difficulty not in _HIGHER_THAN_BEGINNER:
        return
    for path, text in items:
        path_norm = _norm(path)
        text_norm = _norm(text)
        if not any(marker in path_norm for marker in ["nome", "usuario", "operador", "responsavel"]):
            continue
        if _contains_any_name(text_norm, names) and (_contains_token(text_norm, _INCRIMINATING_VERBS) or _contains_token(text_norm, _CRITICAL_CONTEXT)):
            report.add(
                "OBV_001",
                ObviousnessSeverity.WARNING,
                "Log/sistema/escala em dificuldade Intermediário+ usa nome em contexto crítico; prefira código operacional.",
                document=code,
                detail=_clip(text),
                path=path,
            )
            return


def _iter_text(value: Any, path: str) -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        if value.strip():
            yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if str(key).strip() in _INTERNAL_FIELD_NAMES:
                yield child_path, str(key)
            yield from _iter_text(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_text(child, f"{path}[{index}]")


def _norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", without_marks).strip()


def _sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"[.!?;\n]+", text) if sentence.strip()]


def _contains_any_name(text: str, names: set[str]) -> bool:
    return any(re.search(rf"(?<!\w){re.escape(name)}(?!\w)", text) for name in names)


def _contains_token(text: str, tokens: set[str]) -> bool:
    normalized_tokens = {_norm(token) for token in tokens}
    return any(re.search(rf"(?<!\w){re.escape(token)}(?!\w)", text) for token in normalized_tokens)


def _clip(text: str, max_len: int = 180) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= max_len else f"{text[: max_len - 1]}…"
