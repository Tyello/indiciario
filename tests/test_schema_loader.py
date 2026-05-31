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


def _write_schema(path: Path, payload: str) -> Path:
    path.write_text(payload, encoding="utf-8")
    return path


def test_schema_loader_falha_sem_type(tmp_path: Path):
    path = _write_schema(tmp_path / "sem_type.yaml", '{"template": "01_email.html"}')
    with pytest.raises(SchemaLoadError):
        load_schema(path)


def test_schema_loader_falha_sem_template(tmp_path: Path):
    path = _write_schema(tmp_path / "sem_template.yaml", '{"type": "email_narrador"}')
    with pytest.raises(SchemaLoadError):
        load_schema(path)


def test_schema_loader_falha_required_nao_lista(tmp_path: Path):
    path = _write_schema(
        tmp_path / "required_invalido.yaml",
        '{"type": "email_narrador", "template": "01_email.html", "required": "CAMPO"}',
    )
    with pytest.raises(SchemaLoadError):
        load_schema(path)


def test_schema_loader_falha_lists_nao_objeto(tmp_path: Path):
    path = _write_schema(
        tmp_path / "lists_invalido.yaml",
        '{"type": "email_narrador", "template": "01_email.html", "lists": []}',
    )
    with pytest.raises(SchemaLoadError):
        load_schema(path)


def test_schema_loader_falha_type_duplicado(tmp_path: Path):
    _write_schema(tmp_path / "a.yaml", '{"type": "email_narrador", "template": "01_email.html"}')
    _write_schema(tmp_path / "b.yaml", '{"type": "email_narrador", "template": "02_email.html"}')
    with pytest.raises(SchemaLoadError):
        load_all_schemas(tmp_path)
