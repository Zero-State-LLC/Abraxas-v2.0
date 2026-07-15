from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts/canon/aal_viz_yggdrasil_topology.v1.schema.json"
FIXTURE_ROOT = ROOT / "tests/fixtures/aal_viz_yggdrasil_topology_v1"


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _canonical_hash(artifact: dict[str, Any]) -> str:
    return hashlib.sha256(
        _canonical_json(
            {key: value for key, value in artifact.items() if key != "canonical_hash"}
        )
    ).hexdigest()


def _generation_id(artifact: dict[str, Any]) -> str:
    semantic = copy.deepcopy(artifact)
    semantic.pop("canonical_hash", None)
    semantic.pop("temporal_linkage", None)
    generation = semantic["generation"]
    generation.pop("generated_at", None)
    generation.pop("topology_generation_id", None)
    generation.pop("operator_platform_generation_id", None)
    return hashlib.sha256(_canonical_json(semantic)).hexdigest()


def _edge_id(edge: dict[str, Any]) -> str:
    identity = [edge["edge_class"], edge["source"], edge["target"], edge["relation"]]
    return f"edge:{hashlib.sha256(_canonical_json(identity)).hexdigest()}"


def _patch(document: dict[str, Any], patch: dict[str, Any]) -> None:
    target: Any = document
    path = patch["path"]
    for part in path[:-1]:
        target = target[part]
    key = path[-1]
    operation = patch.get("operation", "replace")
    if operation == "replace":
        target[key] = copy.deepcopy(patch["value"])
    elif operation == "append":
        target[key].append(copy.deepcopy(patch["value"]))
    elif operation == "reverse":
        target[key].reverse()
    else:
        raise AssertionError(f"unsupported fixture patch operation: {operation}")


def _fixture_document(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _valid_cases() -> list[dict[str, Any]]:
    fixture = _fixture_document("valid_cases.json")
    cases: list[dict[str, Any]] = []
    for case in fixture["cases"]:
        artifact = copy.deepcopy(fixture["base_artifact"])
        for patch in case.get("patches", []):
            _patch(artifact, patch)
        artifact["generation"]["topology_generation_id"] = case[
            "expected_topology_generation_id"
        ]
        artifact["canonical_hash"] = case["expected_canonical_hash"]
        cases.append({"name": case["name"], "artifact": artifact})
    return cases


def _invalid_cases() -> list[dict[str, Any]]:
    valid = _valid_cases()[0]["artifact"]
    cases: list[dict[str, Any]] = []
    for case in _fixture_document("invalid_cases.json")["cases"]:
        artifact = copy.deepcopy(valid)
        for patch in case.get("patches", []):
            _patch(artifact, patch)
        if case.get("rehash", False):
            artifact["generation"]["topology_generation_id"] = _generation_id(artifact)
            artifact["canonical_hash"] = _canonical_hash(artifact)
        cases.append(
            {
                "name": case["name"],
                "artifact": artifact,
                "expected_error": case["expected_error"],
            }
        )
    return cases


def _semantic_errors(artifact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if artifact.get("canonical_hash") != _canonical_hash(artifact):
        errors.append("canonical hash mismatch")
    generation = artifact.get("generation", {})
    if generation.get("topology_generation_id") != _generation_id(artifact):
        errors.append("topology generation id mismatch")
    sources = artifact.get("source_artifacts", [])
    if sources != sorted(sources, key=lambda item: item.get("id", "")):
        errors.append("source artifacts not canonically ordered")
    for source in sources:
        if source.get("id") != f"source:{source.get('source_key')}":
            errors.append("source identity mismatch")
    findings = artifact.get("validation_findings", [])
    if findings != sorted(findings):
        errors.append("validation findings not canonically ordered")
    payload = artifact.get("payload")
    if not isinstance(payload, dict):
        return errors
    evidence = payload.get("evidence", [])
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])
    for label, records in (("evidence", evidence), ("nodes", nodes), ("edges", edges)):
        ids = [record.get("id") for record in records]
        if ids != sorted(ids):
            errors.append(f"{label} not canonically ordered")
        if len(ids) != len(set(ids)):
            errors.append(f"duplicate {label} id")
    evidence_ids = {record.get("id") for record in evidence}
    node_ids = {record.get("id") for record in nodes}
    for node in nodes:
        if node.get("roles", []) != sorted(node.get("roles", [])):
            errors.append("node roles not canonically ordered")
        if node.get("evidence_refs", []) != sorted(node.get("evidence_refs", [])):
            errors.append("node evidence refs not canonically ordered")
        if not set(node.get("evidence_refs", [])).issubset(evidence_ids):
            errors.append("dangling node evidence reference")
        temporal_ref = node.get("temporal_ref", {})
        if temporal_ref.get("entity_id") != node.get("id"):
            errors.append("node temporal reference mismatch")
    for edge in edges:
        if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
            errors.append("dangling edge endpoint")
        if edge.get("evidence_refs", []) != sorted(edge.get("evidence_refs", [])):
            errors.append("edge evidence refs not canonically ordered")
        if not set(edge.get("evidence_refs", [])).issubset(evidence_ids):
            errors.append("dangling edge evidence reference")
        temporal_ref = edge.get("temporal_ref", {})
        if temporal_ref.get("entity_id") != edge.get("id"):
            errors.append("edge temporal reference mismatch")
        if edge.get("id", "").startswith("edge:") and edge.get("id") != _edge_id(edge):
            errors.append("edge identity mismatch")
    summary = payload.get("summary", {})
    if summary.get("node_count") != len(nodes) or summary.get("edge_count") != len(edges):
        errors.append("summary count mismatch")
    if summary.get("evidence_count") != len(evidence):
        errors.append("summary evidence count mismatch")
    node_class_counts = {
        node_class: sum(1 for node in nodes if node.get("node_class") == node_class)
        for node_class in sorted({node.get("node_class") for node in nodes})
    }
    edge_class_counts = {
        edge_class: sum(1 for edge in edges if edge.get("edge_class") == edge_class)
        for edge_class in sorted({edge.get("edge_class") for edge in edges})
    }
    if summary.get("node_class_counts") != node_class_counts:
        errors.append("summary node class counts mismatch")
    if summary.get("edge_class_counts") != edge_class_counts:
        errors.append("summary edge class counts mismatch")
    return errors


def test_schema_is_valid_draft_2020_12() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_new_edge_identity_fixed_vector() -> None:
    edge = {
        "edge_class": "PRODUCES",
        "source": "interface:core/x.py",
        "target": "contract:python.X",
        "relation": "PRODUCES",
    }
    assert _edge_id(edge) == (
        "edge:f340e8bfc6412e43d721c9247897cf502068e8a1787ff5237d863e10c34ccf86"
    )


def test_valid_contract_fixtures_and_fixed_vectors() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for case in _valid_cases():
        artifact = case["artifact"]
        validator.validate(artifact)
        assert not _semantic_errors(artifact), case["name"]


def test_invalid_contract_fixtures_fail_for_expected_reason() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for case in _invalid_cases():
        schema_errors = sorted(
            validator.iter_errors(case["artifact"]), key=lambda error: list(error.path)
        )
        rendered = " | ".join(
            [*(error.message for error in schema_errors), *_semantic_errors(case["artifact"])]
        )
        assert case["expected_error"] in rendered, (case["name"], rendered)
