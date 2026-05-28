from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_test_vector_schema_plan import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_test_vector_schema_plan,
    compute_chamfer_test_vector_schema_plan_hash,
    default_invalid_schema_groups,
    default_not_computable_schema_groups,
    default_output_contract,
    default_schema_constraints,
    default_schema_layout_plan,
    default_valid_schema_groups,
    default_validation_plan,
    serialize_chamfer_test_vector_schema_plan,
)


def _payload() -> dict[str, object]:
    return {
        "plan_id": "chamfer-test-vector-schema-plan-001",
        "source_fixture_plan_refs": ["ChamferTestVectorFixturePlan.v1:plan-001"],
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "source_baseline_vector_pack_refs": ["MetricOperatorBaselineTestVectorPack.v1:pack-001"],
        "schema_scope": {"schema_family": "MIXED_SCHEMA_PLAN", "intended_lane": "SHADOW", "schema_stage": "SCHEMA_PLAN_ONLY"},
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {"source": "CHAMFER_TEST_VECTOR_SCHEMA_PLAN_v0.1", "evidence_refs": ["ChamferBaselineImplementationPlan.v1:plan-001"], "generated_by": "unit-test", "upstream_schema_refs": ["contracts/canon/chamfer_baseline_implementation_plan.v1.schema.json"]},
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_test_vector_schema_plan(_payload())
    b = build_chamfer_test_vector_schema_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_test_vector_schema_plan(a) == serialize_chamfer_test_vector_schema_plan(b)


def test_default_groups_deterministic() -> None:
    assert default_valid_schema_groups() == default_valid_schema_groups()
    assert default_invalid_schema_groups() == default_invalid_schema_groups()
    assert default_not_computable_schema_groups() == default_not_computable_schema_groups()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["schema_scope"].__setitem__("schema_family", "BAD"), "unknown_schema_family"),
        (lambda p: p["schema_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["schema_scope"].__setitem__("schema_stage", "BAD"), "unknown_schema_stage"),
        (lambda p: p["valid_schema_groups"].append(dict(p["valid_schema_groups"][0])), "duplicate_group_id"),
        (lambda p: p["valid_schema_groups"][0].__setitem__("schema_type", "BAD"), "unknown_schema_type"),
        (lambda p: p["invalid_schema_groups"][0].__setitem__("invalid_reason", "BAD"), "unknown_invalid_reason"),
        (lambda p: p["not_computable_schema_groups"][0].__setitem__("not_computable_reason", "BAD"), "unknown_not_computable_reason"),
        (lambda p: p["not_computable_schema_groups"][0].__setitem__("expected_state", "BAD"), "unknown_expected_state"),
        (lambda p: p["invalid_schema_groups"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
    ],
)
def test_enum_and_duplicate_failures(mutator, err: str) -> None:
    p = _payload()
    p["valid_schema_groups"] = default_valid_schema_groups()
    p["invalid_schema_groups"] = default_invalid_schema_groups()
    p["not_computable_schema_groups"] = default_not_computable_schema_groups()
    mutator(p)
    with pytest.raises(ValueError, match=err):
        build_chamfer_test_vector_schema_plan(p)


def test_locked_maps_and_flags() -> None:
    p = _payload()
    p["schema_layout_plan"] = default_schema_layout_plan()
    p["schema_layout_plan"]["fixture_files_added"] = True
    with pytest.raises(ValueError, match="invalid_schema_layout_plan"):
        build_chamfer_test_vector_schema_plan(p)

    p = _payload()
    p["schema_constraints"] = default_schema_constraints()
    p["schema_constraints"]["metric_values_added"] = True
    with pytest.raises(ValueError, match="invalid_schema_constraints"):
        build_chamfer_test_vector_schema_plan(p)

    p = _payload()
    p["validation_plan"] = default_validation_plan()
    p["validation_plan"]["requires_schema_validation"] = False
    with pytest.raises(ValueError, match="invalid_validation_plan"):
        build_chamfer_test_vector_schema_plan(p)

    p = _payload()
    p["output_contract"] = default_output_contract()
    p["output_contract"]["emits_fixture_files"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_chamfer_test_vector_schema_plan(p)

    p = _payload()
    p["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_chamfer_test_vector_schema_plan(p)


def test_provenance_hash_schema_and_refs() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler metric-value schema-file"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_chamfer_test_vector_schema_plan(p)

    packet = build_chamfer_test_vector_schema_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_test_vector_schema_plan_hash(packet) == compute_chamfer_test_vector_schema_plan_hash(altered)

    changed_payload = _payload()
    changed_payload["schema_scope"]["schema_stage"] = "SCHEMA_LAYOUT_ONLY"
    changed = build_chamfer_test_vector_schema_plan(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_test_vector_schema_plan.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)
    assert all(isinstance(x, str) and x for x in packet["provenance"]["evidence_refs"])
