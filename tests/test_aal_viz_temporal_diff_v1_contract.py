from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts/canon/aal_viz_temporal_diff.v1.schema.json"
FIXTURE_ROOT = ROOT / "tests/fixtures/aal_viz_temporal_diff_v1"


def _canonical_hash(payload: dict[str, Any]) -> str:
    unhashed = {key: value for key, value in payload.items() if key != "canonical_hash"}
    encoded = json.dumps(
        unhashed,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _entry_id(entry: dict[str, Any]) -> str:
    identity = [
        entry["operation"],
        entry["category"],
        entry["entity_id"],
        entry["field_path"],
    ]
    encoded = json.dumps(identity, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def _load_cases(name: str) -> list[dict[str, Any]]:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))["cases"]


def _semantic_errors(artifact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_ids = [entry.get("id") for entry in artifact.get("entries", [])]
    if len(entry_ids) != len(set(entry_ids)):
        errors.append("duplicate entry id")
    if artifact.get("canonical_hash") != _canonical_hash(artifact):
        errors.append("canonical hash mismatch")
    return errors


def test_schema_is_valid_draft_2020_12() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_valid_contract_fixtures_and_fixed_hashes() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for case in _load_cases("valid_cases.json"):
        artifact = case["artifact"]
        validator.validate(artifact)
        assert artifact["canonical_hash"] == _canonical_hash(artifact), case["name"]
        assert artifact["entries"] == sorted(
            artifact["entries"],
            key=lambda entry: (
                entry["category"],
                entry["surface"],
                entry["entity_id"],
                entry["field_path"],
                entry["operation"],
                entry["id"],
            ),
        )
        for entry in artifact["entries"]:
            assert entry["id"] == _entry_id(entry), case["name"]
        changed = [
            entry
            for entry in artifact["entries"]
            if entry["operation"] != "NOT_COMPUTABLE"
        ]
        missing = [
            entry
            for entry in artifact["entries"]
            if entry["operation"] == "NOT_COMPUTABLE"
        ]
        assert artifact["summary"]["total_change_count"] == len(changed)
        assert artifact["summary"]["not_computable_count"] == len(missing)


def test_invalid_contract_fixtures_fail_for_expected_reason() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for case in _load_cases("invalid_cases.json"):
        schema_errors = sorted(
            validator.iter_errors(case["artifact"]), key=lambda error: list(error.path)
        )
        rendered = " | ".join(
            [
                *(error.message for error in schema_errors),
                *_semantic_errors(case["artifact"]),
            ]
        )
        assert rendered, case["name"]
        assert case["expected_error"] in rendered, (case["name"], rendered)


def test_contract_forbids_unchanged_entries() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    artifact = _load_cases("valid_cases.json")[0]["artifact"]
    mutated = json.loads(json.dumps(artifact))
    mutated["entries"] = [
        {
            **_load_cases("valid_cases.json")[1]["artifact"]["entries"][0],
            "operation": "UNCHANGED",
        }
    ]
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(mutated))
    assert errors
