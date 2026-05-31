from pathlib import Path

import pytest

from generator.schema_loader import SchemaLoadError, get_schema_for_type, load_all_schemas, load_schema


def test_schema_loader_carrega_todos_yaml():
    schemas = load_all_schemas()
    for tipo in {
        "email_narrador", "email_institucional", "chat", "boletim", "depoimento",
        "protocolo", "carta", "manual", "glossario", "folha_cruzamento",
        "contrato", "log_acesso", "log_sistema", "escala", "recibo",
        "orcamento", "extrato", "outro",
    }:
        assert tipo in schemas
        assert get_schema_for_type(tipo, schemas)["type"] == tipo


def test_schema_loader_falha_com_yaml_invalido(tmp_path: Path):
    path = tmp_path / "quebrado.yaml"
    path.write_text("type: [\n", encoding="utf-8")
    with pytest.raises(SchemaLoadError):
        load_schema(path)
