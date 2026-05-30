from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geodesic_test_vector_schema_plan import (
    LOCKED_FALSE_FLAGS,
    GeodesicTestVectorSchemaPlanValidationError,
    build_geodesic_test_vector_schema_plan,
    default_invalid_schema_groups,
    default_not_computable_schema_groups,
    default_output_contract,
    default_schema_constraints,
    default_schema_layout_plan,
    default_valid_schema_groups,
    default_validation_plan,
    serialize_geodesic_test_vector_schema_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "geodesic-schema-plan-test-001",
        "source_dossier_refs": [
            "GeodesicDistanceImplementationReadinessDossier.v1:dossier-001"
        ],
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "source_baseline_vector_pack_refs": [
            "MetricOperatorBaselineTestVectorPack.v1:pack-001"
        ],
        "schema_scope": {
            "schema_family": "MIXED_SCHEMA_PLAN",
            "intended_lane": "SHADOW",
            "schema_stage": "SCHEMA_PLAN_ONLY",
        },
        "valid_schema_groups": default_valid_schema_groups(),
        "invalid_schema_groups": default_invalid_schema_groups(),
        "not_computable_schema_groups": default_not_computable_schema_groups(),
        "schema_layout_plan": default_schema_layout_plan(),
        "schema_constraints": default_schema_constraints(),
        "validation_plan": default_validation_plan(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "GEODESIC_TEST_VECTOR_SCHEMA_PLAN_TEST",
            "evidence_refs": [
                "GeodesicDistanceImplementationReadinessDossier.v1:dossier-001"
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/geodesic_test_vector_schema_plan.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_geodesic_test_vector_schema_plan(_payload())
    b = build_geodesic_test_vector_schema_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    assert p["schema_version"] == "GeodesicTestVectorSchemaPlan.v1"


def test_plan_type_fixed() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    assert p["plan_type"] == "GEODESIC_TEST_VECTOR_SCHEMA_PLAN"


def test_operator_id_fixed() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    assert p["operator_id"] == "GEODESIC"


def test_default_valid_schema_groups_non_empty() -> None:
    groups = default_valid_schema_groups()
    assert len(groups) >= 1


def test_default_valid_schema_groups_count() -> None:
    assert len(default_valid_schema_groups()) == 5


def test_default_valid_groups_have_self_loop_case() -> None:
    descs = [g["description"].lower() for g in default_valid_schema_groups()]
    assert any("self" in d or "source_node equals target" in d for d in descs)


def test_default_invalid_schema_groups_non_empty() -> None:
    groups = default_invalid_schema_groups()
    assert len(groups) >= 1


def test_default_invalid_groups_cover_negative_weight() -> None:
    reasons = [g["invalid_reason"] for g in default_invalid_schema_groups()]
    assert "NEGATIVE_EDGE_WEIGHT" in reasons


def test_default_not_computable_groups_non_empty() -> None:
    groups = default_not_computable_schema_groups()
    assert len(groups) >= 1


def test_default_not_computable_groups_cover_disconnected() -> None:
    reasons = [g["not_computable_reason"] for g in default_not_computable_schema_groups()]
    assert "DISCONNECTED_GRAPH" in reasons
    assert "EMPTY_INPUT" in reasons


def test_schema_constraints_no_math_added() -> None:
    c = default_schema_constraints()
    assert c["geodesic_math_added"] is False
    assert c["expected_geodesic_distances_added"] is False
    assert c["fixture_files_generated"] is False
    assert c["metric_values_added"] is False


def test_schema_layout_plan_no_files_added() -> None:
    s = default_schema_layout_plan()
    assert s["fixture_files_added"] is False
    assert s["schema_files_added"] is False
    assert s["expected_metric_values_declared"] is False
    assert s["schema_directory_declared"] is True


def test_output_contract_no_metric_emission() -> None:
    c = default_output_contract()
    assert c["emits_metric_values"] is False
    assert c["emits_fixture_files"] is False
    assert c["emits_expected_geodesic_distances"] is False
    assert c["emits_schema_group_metadata"] is True
    assert c["emits_schema_plan"] is True


def test_all_governance_flags_false() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["governance_flags"][flag] is False


def test_canonical_hash_64_hex() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_valid_groups_sorted_by_group_id() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    ids = [g["group_id"] for g in p["valid_schema_groups"]]
    assert ids == sorted(ids)


def test_invalid_groups_sorted_by_group_id() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    ids = [g["group_id"] for g in p["invalid_schema_groups"]]
    assert ids == sorted(ids)


def test_not_computable_groups_sorted_by_group_id() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    ids = [g["group_id"] for g in p["not_computable_schema_groups"]]
    assert ids == sorted(ids)


def test_serialize_is_valid_json() -> None:
    p = build_geodesic_test_vector_schema_plan(_payload())
    raw = serialize_geodesic_test_vector_schema_plan(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "GeodesicTestVectorSchemaPlan.v1"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["schema_scope"].__setitem__("schema_family", "BAD"),
            "unknown_schema_family",
        ),
        (
            lambda p: p["schema_scope"].__setitem__("intended_lane", "BAD"),
            "unknown_intended_lane",
        ),
        (
            lambda p: p["schema_scope"].__setitem__("schema_stage", "BAD"),
            "unknown_schema_stage",
        ),
        (
            lambda p: p.__setitem__("valid_schema_groups", []),
            "valid_schema_groups_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("invalid_schema_groups", []),
            "invalid_schema_groups_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("not_computable_schema_groups", []),
            "not_computable_schema_groups_must_be_non_empty",
        ),
        (
            lambda p: p["governance_flags"].__setitem__("execution_authority", True),
            "authority_lock_must_be_false:execution_authority",
        ),
        (
            lambda p: p["provenance"].__setitem__(
                "generated_by", "bad-geodesic-distance-ref"
            ),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(GeodesicTestVectorSchemaPlanValidationError, match=err):
        build_geodesic_test_vector_schema_plan(payload)


def test_committed_artifact_parseable() -> None:
    path = Path(
        "out/metric_operator/geodesic_test_vector_schema_plan_001.latest.json"
    )
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "GeodesicTestVectorSchemaPlan.v1"
    assert data["operator_id"] == "GEODESIC"
    assert len(data["canonical_hash"]) == 64
