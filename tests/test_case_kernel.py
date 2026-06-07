import json
from dataclasses import replace
from pathlib import Path

from generator.case_kernel import (
    CaseKernel,
    EnvelopeKernel,
    extract_case_kernel,
    validate_case_kernel,
)
from generator.models import Blueprint


ROOT = Path(__file__).resolve().parents[1]


def load_blueprint(path: str) -> Blueprint:
    return Blueprint(**json.loads((ROOT / path).read_text(encoding="utf-8")))


def finding_codes(kernel: CaseKernel) -> set[str]:
    return {finding.code for finding in validate_case_kernel(kernel)}


def test_extracts_case_kernel_from_iniciante_canonical() -> None:
    blueprint = load_blueprint("examples/caso_canonico_iniciante.json")

    kernel = extract_case_kernel(blueprint)

    assert kernel.titulo == "O Desvio da Reserva Mirante"
    assert kernel.dificuldade == "iniciante"
    assert kernel.pergunta_publica
    assert kernel.verdade_final
    assert kernel.hipotese_e1
    assert kernel.recontextualizacao_e2
    assert len(kernel.envelopes) == blueprint.formato_envelopes
    assert kernel.evidencias_obrigatorias


def test_extracts_case_kernel_from_intermediario_canonical() -> None:
    blueprint = load_blueprint("examples/caso_canonico_intermediario.json")

    kernel = extract_case_kernel(blueprint)

    assert kernel.titulo == "O Último Brinde do Hotel Aurora"
    assert kernel.dificuldade == "intermediario"
    assert kernel.pergunta_publica
    assert kernel.verdade_final
    assert kernel.hipotese_e1
    assert kernel.recontextualizacao_e2
    assert kernel.red_herrings


def test_validation_returns_findings_list_without_exception() -> None:
    blueprint = load_blueprint("examples/caso_canonico_iniciante.json")
    kernel = extract_case_kernel(blueprint)

    findings = validate_case_kernel(kernel)

    assert isinstance(findings, list)
    assert all(finding.code.startswith("CK_") for finding in findings)


def test_canonical_cases_do_not_generate_unexpected_critical_findings() -> None:
    for path in [
        "examples/caso_canonico_iniciante.json",
        "examples/caso_canonico_intermediario.json",
    ]:
        kernel = extract_case_kernel(load_blueprint(path))
        findings = validate_case_kernel(kernel)

        assert [finding for finding in findings if finding.severity == "critical"] == []
        assert "CK_010" not in {finding.code for finding in findings}


def test_artificial_case_without_public_question_generates_ck_001() -> None:
    kernel = extract_case_kernel(load_blueprint("examples/caso_canonico_iniciante.json"))
    weak_kernel = replace(kernel, pergunta_publica="")

    assert "CK_001" in finding_codes(weak_kernel)


def test_artificial_two_envelope_case_without_e2_recontextualization_generates_ck_005() -> None:
    kernel = extract_case_kernel(load_blueprint("examples/caso_canonico_intermediario.json"))
    two_envelope_kernel = replace(
        kernel,
        recontextualizacao_e2="",
        envelopes=(
            EnvelopeKernel("E1", "Pergunta E1?", "Resposta E1", "Função E1", "Avança E1"),
            EnvelopeKernel("E2", "Pergunta E2?", "Resposta E2", "Função E2", "Avança E2"),
        ),
    )

    assert "CK_005" in finding_codes(two_envelope_kernel)


def test_case_kernel_does_not_mutate_blueprint_or_write_files(tmp_path: Path) -> None:
    blueprint = load_blueprint("examples/caso_canonico_iniciante.json")
    before = blueprint.model_dump(mode="json")
    before_files = set(tmp_path.iterdir())

    kernel = extract_case_kernel(blueprint)
    findings = validate_case_kernel(kernel)

    assert blueprint.model_dump(mode="json") == before
    assert isinstance(findings, list)
    assert set(tmp_path.iterdir()) == before_files
