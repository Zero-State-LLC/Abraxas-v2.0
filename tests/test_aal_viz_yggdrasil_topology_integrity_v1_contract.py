from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "contracts/canon/aal_viz_yggdrasil_topology_integrity.v1.schema.json"
)
FIXTURE_ROOT = ROOT / "tests/fixtures/aal_viz_yggdrasil_topology_integrity_v1"
SEVERITY_BY_TYPE = {
    "GENERATION_MISMATCH": "HIGH",
    "INFERRED_LINK": "INFO",
    "MISSING_EVIDENCE": "LOW",
    "SECTION_NOT_COMPUTABLE": "NOT_COMPUTABLE",
    "SOURCE_INTEGRITY_GAP": "HIGH",
    "STALE_ENTITY": "MEDIUM",
    "TEMPORAL_REMOVAL": "MEDIUM",
    "TEMPORAL_WEAKENING": "MEDIUM",
    "UNRESOLVED_ENTITY": "MEDIUM",
}
TEMPORAL_TYPES = {"TEMPORAL_REMOVAL", "TEMPORAL_WEAKENING"}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _canonical_hash(artifact: dict[str, Any]) -> str:
    preimage = {key: value for key, value in artifact.items() if key != "canonical_hash"}
    return hashlib.sha256(_canonical_json(preimage)).hexdigest()


def _generation_id(artifact: dict[str, Any]) -> str:
    semantic = copy.deepcopy(artifact)
    semantic.pop("canonical_hash", None)
    semantic["generation"].pop("generated_at", None)
    semantic["generation"].pop("integrity_generation_id", None)
    return hashlib.sha256(_canonical_json(semantic)).hexdigest()


def _finding_id(finding: dict[str, Any], topology_generation_id: str) -> str:
    entity_ref = finding.get("entity_ref") or {}
    identity = [
        finding["finding_type"],
        entity_ref.get("category"),
        entity_ref.get("entity_id"),
        finding["subject_key"],
        topology_generation_id,
    ]
    return f"finding:{hashlib.sha256(_canonical_json(identity)).hexdigest()}"


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
    elif operation == "prepend":
        target[key].insert(0, copy.deepcopy(patch["value"]))
    elif operation == "append_copy":
        target[key].append(copy.deepcopy(target[key][patch["source_index"]]))
    elif operation == "reverse":
        target[key].reverse()
    else:
        raise AssertionError(f"unsupported fixture patch operation: {operation}")


def _fixture_document(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _assign_finding_ids(artifact: dict[str, Any]) -> list[str]:
    payload = artifact.get("payload")
    if not isinstance(payload, dict):
        return []
    topology_id = artifact["generation"]["topology_generation_id"]
    if not isinstance(topology_id, str):
        return []
    for finding in payload["findings"]:
        finding["id"] = _finding_id(finding, topology_id)
    return [finding["id"] for finding in payload["findings"]]


def _valid_cases() -> list[dict[str, Any]]:
    fixture = _fixture_document("valid_cases.json")
    cases: list[dict[str, Any]] = []
    for case in fixture["cases"]:
        artifact = copy.deepcopy(fixture["base_artifact"])
        for patch in case.get("patches", []):
            _patch(artifact, patch)
        finding_ids = _assign_finding_ids(artifact)
        artifact["generation"]["integrity_generation_id"] = case[
            "expected_integrity_generation_id"
        ]
        artifact["canonical_hash"] = case["expected_canonical_hash"]
        cases.append(
            {
                "name": case["name"],
                "artifact": artifact,
                "finding_ids": finding_ids,
                "expected_finding_ids": case["expected_finding_ids"],
            }
        )
    return cases


def _invalid_cases() -> list[dict[str, Any]]:
    valid = _valid_cases()[1]["artifact"]
    cases: list[dict[str, Any]] = []
    for case in _fixture_document("invalid_cases.json")["cases"]:
        artifact = copy.deepcopy(valid)
        for patch in case.get("patches", []):
            _patch(artifact, patch)
        if case.get("rehash", False):
            _assign_finding_ids(artifact)
            artifact["generation"]["integrity_generation_id"] = _generation_id(
                artifact
            )
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
    if generation.get("integrity_generation_id") != _generation_id(artifact):
        errors.append("integrity generation id mismatch")
    sources = artifact.get("source_artifacts", [])
    if sources != sorted(sources, key=lambda source: source.get("id", "")):
        errors.append("source artifacts not canonically ordered")
    source_ids = {source.get("id") for source in sources}
    temporal_source = next(
        (source for source in sources if source.get("source_key") == "temporal_diff"),
        None,
    )
    findings = artifact.get("validation_findings", [])
    if findings != sorted(findings):
        errors.append("validation findings not canonically ordered")
    payload = artifact.get("payload")
    if not isinstance(payload, dict):
        return errors
    records = payload.get("findings", [])
    ids = [finding.get("id") for finding in records]
    if ids != sorted(ids):
        errors.append("findings not canonically ordered")
    if len(ids) != len(set(ids)):
        errors.append("duplicate finding id")
    for finding in records:
        expected_severity = SEVERITY_BY_TYPE.get(finding.get("finding_type"))
        if finding.get("severity") != expected_severity:
            errors.append("severity mismatch")
        topology_id = generation.get("topology_generation_id")
        if isinstance(topology_id, str) and finding.get("id") != _finding_id(
            finding, topology_id
        ):
            errors.append("finding identity mismatch")
        evidence_refs = finding.get("evidence_refs", [])
        if evidence_refs != sorted(evidence_refs):
            errors.append("evidence references not canonically ordered")
        if any(
            reference.startswith("source:") and reference not in source_ids
            for reference in evidence_refs
        ):
            errors.append("dangling evidence reference")
        binding = finding.get("generation_binding", {})
        for key in (
            "topology_generation_id",
            "operator_platform_generation_id",
            "temporal_diff_generation_id",
        ):
            if binding.get(key) != generation.get(key):
                errors.append("finding generation binding mismatch")
        if finding.get("finding_type") in TEMPORAL_TYPES:
            temporal_matched = (
                temporal_source is not None
                and temporal_source.get("integrity_state") == "VERIFIED"
                and generation.get("temporal_diff_generation_id") is not None
                and generation.get("temporal_diff_generation_id")
                == generation.get("operator_platform_generation_id")
            )
            if not temporal_matched:
                errors.append("temporal conclusion without matched evidence")
        if finding.get("finding_type") == "GENERATION_MISMATCH" and (
            generation.get("temporal_diff_generation_id")
            == generation.get("operator_platform_generation_id")
        ):
            errors.append("generation mismatch finding without mismatch")
        expected_computability = (
            "NOT_COMPUTABLE"
            if finding.get("finding_type") == "SECTION_NOT_COMPUTABLE"
            else "COMPUTABLE"
        )
        if finding.get("computability") != expected_computability:
            errors.append("finding computability mismatch")
    summary = payload.get("summary", {})
    entity_ids = {
        (
            finding.get("entity_ref", {}).get("category"),
            finding.get("entity_ref", {}).get("entity_id"),
        )
        for finding in records
        if isinstance(finding.get("entity_ref"), dict)
    }
    expected = {
        "finding_count": len(records),
        "affected_entity_count": len(entity_ids),
        "non_computable_count": sum(
            finding.get("computability") == "NOT_COMPUTABLE" for finding in records
        ),
        "severity_counts": dict(
            sorted(Counter(finding.get("severity") for finding in records).items())
        ),
        "type_counts": dict(
            sorted(Counter(finding.get("finding_type") for finding in records).items())
        ),
    }
    if summary != expected:
        errors.append("summary count mismatch")
    return errors


def test_schema_is_valid_draft_2020_12() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_finding_identity_fixed_vector() -> None:
    finding = {
        "finding_type": "UNRESOLVED_ENTITY",
        "subject_key": "node:example",
        "entity_ref": {"category": "TOPOLOGY_NODE", "entity_id": "node:example"},
    }
    assert _finding_id(finding, "a" * 64) == (
        "finding:f9068b8117c9fbce10a0516ea917a01e03375a48d5acf2b7e0d1fcd2f6a82f43"
    )


def test_valid_contract_fixtures_and_fixed_vectors() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    for case in _valid_cases():
        artifact = case["artifact"]
        validator.validate(artifact)
        assert case["finding_ids"] == case["expected_finding_ids"], case["name"]
        assert not _semantic_errors(artifact), case["name"]


def test_invalid_contract_fixtures_fail_for_expected_reason() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    for case in _invalid_cases():
        schema_errors = sorted(
            validator.iter_errors(case["artifact"]), key=lambda error: list(error.path)
        )
        rendered = " | ".join(
            [
                *(error.message for error in schema_errors),
                *_semantic_errors(case["artifact"]),
            ]
        )
        assert case["expected_error"] in rendered, (case["name"], rendered)
