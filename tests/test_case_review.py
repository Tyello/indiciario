import json
import subprocess
import sys
from pathlib import Path

from generator.case_review import render_review, review_case, review_case_file
from generator.models import Blueprint

ROOT = Path(__file__).resolve().parents[1]
INICIANTE = ROOT / "examples" / "caso_canonico_iniciante.json"
INTERMEDIARIO = ROOT / "examples" / "caso_canonico_intermediario.json"


def _blueprint_data(path: Path = INICIANTE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _finding_codes(review) -> set[str]:
    return {finding.code for finding in review.findings} | {
        finding.code for finding in review.kernel_findings
    }


def test_gera_review_do_canonico_iniciante():
    review = review_case_file(INICIANTE)

    assert review.title == "O Desvio da Reserva Mirante"
    assert review.kernel.pergunta_publica
    assert review.status in {
        "READY_FOR_BASELINE",
        "READY_FOR_PLAYTEST",
        "NEEDS_EDITORIAL_REVIEW",
    }


def test_gera_review_do_canonico_intermediario():
    review = review_case_file(INTERMEDIARIO)

    assert review.title == "O Último Brinde do Hotel Aurora"
    assert review.kernel.recontextualizacao_e2
    assert review.status in {
        "READY_FOR_BASELINE",
        "READY_FOR_PLAYTEST",
        "NEEDS_EDITORIAL_REVIEW",
    }


def test_saida_markdown_contem_secoes_esperadas():
    markdown = render_review(review_case_file(INICIANTE), "markdown")

    for section in [
        "# Case Review — O Desvio da Reserva Mirante",
        "## Resumo",
        "## Case Kernel",
        "## Solvabilidade",
        "## Progressão por envelope",
        "## Red herrings",
        "## Dificuldade",
        "## Prontidão para playtest",
    ]:
        assert section in markdown


def test_saida_json_contem_status_e_findings():
    payload = json.loads(render_review(review_case_file(INICIANTE), "json"))

    assert payload["status"]
    assert "findings" in payload
    assert "kernel_findings" in payload
    assert payload["playtest_metrics"]["summary"]["difficulty_declared"] == "iniciante"


def test_cli_funciona_com_stdout():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.case_review",
            str(INICIANTE),
            "--format",
            "markdown",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "# Case Review — O Desvio da Reserva Mirante" in result.stdout
    assert "## Prontidão para playtest" in result.stdout


def test_cli_funciona_com_output(tmp_path):
    output = tmp_path / "case_review_mirante.md"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.case_review",
            str(INICIANTE),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.exists()
    assert "## Solvabilidade" in output.read_text(encoding="utf-8")


def test_caso_artificial_ruim_gera_findings():
    data = _blueprint_data()
    data["contratos_evidencia"] = []
    data["red_herrings"][0]["motivo_aparente"] = "É culpado e confessa o desvio."
    data["red_herrings"][0]["documento_descarte"] = "E9-99"
    data["objetivos_por_envelope"][0]["pergunta_diegetica"] = "Quem é o culpado final?"
    data["objetivos_por_envelope"][0]["resposta_esperada"] = "Identificar o culpado."

    review = review_case(Blueprint(**data))
    codes = _finding_codes(review)

    assert "CR_SOLV_001" in codes
    assert "CR_SOLV_004" in codes
    assert "CR_RH_002" in codes
    assert "CR_RH_003" in codes
    assert "CR_PROG_002" in codes


def test_strict_nao_falha_nos_canonicos_atuais_sem_motivo_critico():
    for path in [INICIANTE, INTERMEDIARIO]:
        result = subprocess.run(
            [sys.executable, "-m", "scripts.case_review", str(path), "--strict"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stdout + result.stderr
