"""Carregamento de schemas técnicos de conteúdo por tipo de documento."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - fallback para ambientes sem dependências instaladas.
    yaml = None  # type: ignore[assignment]

SCHEMAS_DIR = Path(__file__).parent / "schemas"

_SCHEMA_LIST_FIELDS = {"required", "optional", "required_when", "hidden_allowed", "html_fields"}


class SchemaLoadError(ValueError):
    """Erro claro ao carregar ou validar um schema YAML."""


def load_schema(path: Path) -> dict[str, Any]:
    """Carrega um schema YAML e valida sua estrutura mínima."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SchemaLoadError(f"Não foi possível ler schema {path}: {exc}") from exc

    try:
        if yaml is not None:
            raw = yaml.safe_load(text)
        else:
            raw = json.loads(text)
    except Exception as exc:  # noqa: BLE001 - mensagem clara para YAML/JSON inválido.
        raise SchemaLoadError(f"YAML inválido em {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise SchemaLoadError(f"Schema {path} deve conter um objeto YAML no topo.")

    schema: dict[str, Any] = raw
    for field in ("type", "template"):
        if not isinstance(schema.get(field), str) or not schema[field].strip():
            raise SchemaLoadError(f"Schema {path} precisa declarar '{field}' como string não vazia.")

    for field in _SCHEMA_LIST_FIELDS:
        value = schema.get(field, [])
        if value is None:
            schema[field] = []
            continue
        if not isinstance(value, list):
            raise SchemaLoadError(f"Campo '{field}' em {path} deve ser uma lista.")

    lists = schema.get("lists", {})
    if lists is None:
        schema["lists"] = {}
    elif not isinstance(lists, dict):
        raise SchemaLoadError(f"Campo 'lists' em {path} deve ser um objeto.")

    for rule in schema.get("required_when", []):
        _validate_required_when(rule, path)

    for list_name, list_rule in schema.get("lists", {}).items():
        if not isinstance(list_name, str) or not isinstance(list_rule, dict):
            raise SchemaLoadError(f"Regra de lista inválida em {path}: {list_name!r}.")
        if "item_required" in list_rule and not isinstance(list_rule["item_required"], list):
            raise SchemaLoadError(f"'item_required' de {list_name} em {path} deve ser lista.")
        if "required_when" in list_rule:
            _validate_required_when({"when": list_rule["required_when"], "required": []}, path)

    return schema


def _validate_required_when(rule: Any, path: Path) -> None:
    if not isinstance(rule, dict):
        raise SchemaLoadError(f"Regra required_when inválida em {path}: deve ser objeto.")
    when = rule.get("when")
    if not isinstance(when, dict) or not isinstance(when.get("field"), str):
        raise SchemaLoadError(f"Regra required_when em {path} precisa de when.field.")
    if "required" in rule and not isinstance(rule["required"], list):
        raise SchemaLoadError(f"Regra required_when em {path} precisa de required como lista.")


def load_all_schemas(schema_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Carrega todos os schemas YAML do diretório informado ou do pacote."""
    directory = schema_dir or SCHEMAS_DIR
    if not directory.exists():
        raise SchemaLoadError(f"Diretório de schemas não encontrado: {directory}")

    schemas: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.glob("*.yaml")):
        schema = load_schema(path)
        tipo = schema["type"]
        if tipo in schemas:
            raise SchemaLoadError(f"Schema duplicado para tipo '{tipo}' em {path}.")
        schemas[tipo] = schema
    return schemas


def get_schema_for_type(tipo: str, schemas: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Retorna o schema de um tipo, se existir."""
    return schemas.get(tipo)
