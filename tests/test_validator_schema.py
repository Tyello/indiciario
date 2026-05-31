import json
import subprocess
import sys
from pathlib import Path

from generator.models import TipoDocumento
from generator.validator import BlueprintValidator
from tests.test_generator_validator import blueprint_valido

ROOT = Path(__file__).resolve().parents[1]


def _validar_doc(mutator):
    bp = blueprint_valido()
    doc = next(d for d in bp.documentos if d.tipo == TipoDocumento.EMAIL_N)
    mutator(doc.conteudo)
    return BlueprintValidator(bp).validar()


def test_campo_required_ausente_gera_erro():
    resultado = _validar_doc(lambda c: c.pop("ASSUNTO"))
    assert any(e.codigo == "CONT_003" and e.documento == "E1-02" for e in resultado.criticos)


def test_campo_optional_ausente_nao_gera_erro():
    resultado = _validar_doc(lambda c: c.pop("TOTAL_ANEXOS", None))
    assert not any(e.documento == "E1-02" for e in resultado.criticos)


def test_required_when_exige_campo_quando_condicao_verdadeira():
    def mut(c):
        c["ANEXOS"] = True
        c.pop("CADA_ANEXO", None)
    resultado = _validar_doc(mut)
    assert any(e.codigo == "CONT_REQUIRED_WHEN_001" and e.documento == "E1-02" for e in resultado.criticos)


def test_required_when_nao_exige_campo_quando_condicao_falsa():
    def mut(c):
        c["ANEXOS"] = False
        c.pop("CADA_ANEXO", None)
        c.pop("TOTAL_ANEXOS", None)
    resultado = _validar_doc(mut)
    assert not any(e.documento == "E1-02" for e in resultado.criticos)


def test_lista_obrigatoria_vazia_gera_erro():
    bp = blueprint_valido()
    doc = next(d for d in bp.documentos if d.tipo == TipoDocumento.LOG_ACESSO)
    doc.conteudo["REGISTROS"] = []
    resultado = BlueprintValidator(bp).validar()
    assert any(e.codigo == "CONT_004" and e.documento == doc.codigo for e in resultado.criticos)


def test_item_de_lista_sem_campo_obrigatorio_gera_erro():
    bp = blueprint_valido()
    doc = next(d for d in bp.documentos if d.tipo == TipoDocumento.LOG_ACESSO)
    doc.conteudo["REGISTROS"][0].pop("PORTA")
    resultado = BlueprintValidator(bp).validar()
    assert any(e.codigo == "CONT_ITEM_001" and e.documento == doc.codigo for e in resultado.criticos)


def test_conteudo_generico_em_required_gera_erro():
    resultado = _validar_doc(lambda c: c.update({"ASSUNTO": "CONTEUDO_GENERICO"}))
    assert any(e.codigo == "CONT_003" and e.documento == "E1-02" for e in resultado.criticos)


def test_showcase_tecnico_valida_sem_criticos():
    path = ROOT / "examples" / "showcase_tecnico.json"
    assert path.exists()
    result = subprocess.run(
        [sys.executable, "generator/validator.py", str(path), "--json"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    output = json.loads(result.stdout)
    assert output["criticos"] == []
