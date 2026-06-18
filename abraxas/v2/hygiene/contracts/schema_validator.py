from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


def schema_dir() -> Path:
    return Path(__file__).resolve().parent / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    path = schema_dir() / name
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(schema_name: str, payload: dict[str, Any]) -> list[str]:
    schema = load_schema(schema_name)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda item: item.path)
    return [error.message for error in errors]
