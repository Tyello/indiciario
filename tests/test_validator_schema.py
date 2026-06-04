import json
import subprocess
import sys
from pathlib import Path

import pytest

from generator.models import Blueprint, TipoDocumento
from generator.validator import BlueprintValidator
from tests.test_generator_validator import CONTEUDO_CARTA_VALIDO, blueprint_valido

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


def test_caso_canonico_iniciante_valida_email_e1_02_com_copia():
    path = ROOT / "examples" / "caso_canonico_iniciante.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    resultado = BlueprintValidator(Blueprint(**data)).validar()

    assert not any(
        e.documento == "E1-02" and "COPIA" in e.mensagem
        for e in resultado.criticos
    )
    assert not any(
        e.documento == "E1-02" and e.codigo.startswith("CONT_")
        for e in resultado.criticos
    )


def _validar_email_anexos(valor):
    def mut(c):
        c["ANEXOS"] = valor
        c.pop("CADA_ANEXO", None)
        c.pop("TOTAL_ANEXOS", None)

    return _validar_doc(mut)


@pytest.mark.parametrize("valor", [False, "false", "não", "nao", "no", "0", 0, "", None])
def test_required_when_bool_falso_normalizado_nao_exige_anexos(valor):
    resultado = _validar_email_anexos(valor)
    assert not any(e.codigo == "CONT_REQUIRED_WHEN_001" and e.documento == "E1-02" for e in resultado.criticos)


@pytest.mark.parametrize("valor", [True, "true", "sim", "yes", "1", 1])
def test_required_when_bool_verdadeiro_normalizado_exige_anexos(valor):
    resultado = _validar_email_anexos(valor)
    assert any(e.codigo == "CONT_REQUIRED_WHEN_001" and e.documento == "E1-02" for e in resultado.criticos)


def test_tipo_outro_valido_usa_schema_e_mantem_aviso_fallback():
    bp = blueprint_valido()
    doc = bp.documentos[0]
    doc.tipo = TipoDocumento.OUTRO
    doc.conteudo = dict(CONTEUDO_CARTA_VALIDO)

    resultado = BlueprintValidator(bp).validar()

    assert any(e.codigo == "CONT_002" and e.documento == doc.codigo for e in resultado.avisos)
    assert not any(e.documento == doc.codigo and e.codigo.startswith("CONT_") for e in resultado.criticos)


def test_tipo_outro_invalido_nao_pula_schema():
    bp = blueprint_valido()
    doc = bp.documentos[0]
    doc.tipo = TipoDocumento.OUTRO
    doc.conteudo = {"CORPO_CARTA": "<p>Texto insuficiente.</p>"}

    resultado = BlueprintValidator(bp).validar()

    assert any(e.codigo == "CONT_002" and e.documento == doc.codigo for e in resultado.avisos)
    assert any(e.codigo == "CONT_003" and e.documento == doc.codigo for e in resultado.criticos)


def test_email_schema_exige_copia():
    resultado = _validar_doc(lambda c: c.pop("COPIA", None))
    assert any(e.codigo == "CONT_003" and e.documento == "E1-02" for e in resultado.criticos)


def test_email_schema_rejeita_copia_com_lixo_tecnico_como_required():
    resultado = _validar_doc(lambda c: c.update({"COPIA": "CONTEUDO_GENERICO"}))
    assert any(e.codigo == "CONT_003" and e.documento == "E1-02" for e in resultado.criticos)


def test_required_vence_hidden_allowed():
    bp = blueprint_valido()
    doc = next(d for d in bp.documentos if d.tipo == TipoDocumento.EMAIL_N)
    doc.conteudo.pop("ASSUNTO")
    validator = BlueprintValidator(bp)
    validator._schemas["email_narrador"].setdefault("hidden_allowed", []).append("ASSUNTO")

    resultado = validator.validar()

    assert any(e.codigo == "CONT_003" and e.documento == doc.codigo for e in resultado.criticos)
