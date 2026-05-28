from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_valid_fixture_implementation_plan import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_valid_fixture_implementation_plan,
    compute_chamfer_valid_fixture_implementation_plan_hash,
    default_deterministic_ordering_plan,
    default_fixture_constraints,
    default_fixture_manifest_plan,
    default_output_contract,
    default_valid_fixture_cases,
    default_validation_plan,
    serialize_chamfer_valid_fixture_implementation_plan,
)


def _payload() -> dict[str, object]:
    return {
        "plan_id": "chamfer-valid-fixture-implementation-plan-001",
        "source_fixture_plan_refs": ["ChamferTestVectorFixturePlan.v1:plan-001"],
        "source_schema_plan_refs": ["ChamferTestVectorSchemaPlan.v1:plan-001"],
        "source_baseline_implementation_plan_refs": ["ChamferBaselineImplementationPlan.v1:plan-001"],
        "valid_fixture_scope": {
            "fixture_family": "MIXED_VALID_FIXTURE_PLAN",
            "intended_lane": "SHADOW",
            "implementation_stage": "IMPLEMENTATION_PLAN_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "CHAMFER_VALID_FIXTURE_IMPLEMENTATION_PLAN_v0.1",
            "evidence_refs": ["ChamferTestVectorSchemaPlan.v1:plan-001"],
            "generated_by": "unit-test",
            "upstream_schema_refs": ["contracts/canon/chamfer_test_vector_schema_plan.v1.schema.json"],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_valid_fixture_implementation_plan(_payload())
    b = build_chamfer_valid_fixture_implementation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_valid_fixture_implementation_plan(a) == serialize_chamfer_valid_fixture_implementation_plan(b)


def test_default_cases_deterministic() -> None:
    assert default_valid_fixture_cases() == default_valid_fixture_cases()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["valid_fixture_scope"].__setitem__("fixture_family", "BAD"), "unknown_fixture_family"),
        (lambda p: p["valid_fixture_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["valid_fixture_scope"].__setitem__("implementation_stage", "BAD"), "unknown_implementation_stage"),
        (lambda p: p["valid_fixture_cases"].append(dict(p["valid_fixture_cases"][0])), "duplicate_case_id"),
        (lambda p: p["valid_fixture_cases"][0].__setitem__("case_type", "BAD"), "unknown_case_type"),
        (lambda p: p["valid_fixture_cases"][0].__setitem__("coordinate_space", "BAD"), "unknown_coordinate_space"),
        (lambda p: p["valid_fixture_cases"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
        (lambda p: p["valid_fixture_cases"][0].__setitem__("dimensionality", 0), "invalid_dimensionality"),
    ],
)
def test_case_and_scope_failures(mutator, err: str) -> None:
    payload = _payload()
    payload["valid_fixture_cases"] = default_valid_fixture_cases()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_chamfer_valid_fixture_implementation_plan(payload)


def test_locked_maps_and_flags() -> None:
    p = _payload()
    p["fixture_manifest_plan"] = default_fixture_manifest_plan()
    p["fixture_manifest_plan"]["manifest_file_added"] = True
    with pytest.raises(ValueError, match="invalid_fixture_manifest_plan"):
        build_chamfer_valid_fixture_implementation_plan(p)

    p = _payload()
    p["deterministic_ordering_plan"] = default_deterministic_ordering_plan()
    p["deterministic_ordering_plan"]["nondeterministic_ordering_allowed"] = True
    with pytest.raises(ValueError, match="invalid_deterministic_ordering_plan"):
        build_chamfer_valid_fixture_implementation_plan(p)

    p = _payload()
    p["validation_plan"] = default_validation_plan()
    p["validation_plan"]["requires_schema_validation"] = False
    with pytest.raises(ValueError, match="invalid_validation_plan"):
        build_chamfer_valid_fixture_implementation_plan(p)

    p = _payload()
    p["fixture_constraints"] = default_fixture_constraints()
    p["fixture_constraints"]["expected_distances_added"] = True
    with pytest.raises(ValueError, match="invalid_fixture_constraints"):
        build_chamfer_valid_fixture_implementation_plan(p)

    p = _payload()
    p["output_contract"] = default_output_contract()
    p["output_contract"]["emits_manifest_file"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_chamfer_valid_fixture_implementation_plan(p)

    p = _payload()
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_chamfer_valid_fixture_implementation_plan(p)


def test_provenance_hash_change_and_schema() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime fixture-file expected-distance"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_chamfer_valid_fixture_implementation_plan(p)

    packet = build_chamfer_valid_fixture_implementation_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_valid_fixture_implementation_plan_hash(packet) == compute_chamfer_valid_fixture_implementation_plan_hash(altered)

    changed_payload = _payload()
    changed_payload["valid_fixture_scope"]["implementation_stage"] = "MANIFEST_PLAN_ONLY"
    changed = build_chamfer_valid_fixture_implementation_plan(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_valid_fixture_implementation_plan.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)
    assert all(isinstance(x, str) and x for x in packet["provenance"]["evidence_refs"])
