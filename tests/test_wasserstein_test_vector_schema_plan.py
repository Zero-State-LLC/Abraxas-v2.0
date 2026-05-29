from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.wasserstein_test_vector_schema_plan import (
    LOCKED_FALSE_FLAGS,
    build_wasserstein_test_vector_schema_plan,
    compute_wasserstein_test_vector_schema_plan_hash,
    default_invalid_schema_groups,
    default_not_computable_schema_groups,
    default_output_contract,
    default_schema_constraints,
    default_schema_layout_plan,
    default_valid_schema_groups,
    default_validation_plan,
    serialize_wasserstein_test_vector_schema_plan,
)


def _payload() -> dict[str, object]:
    return {
        "plan_id": "wasserstein_test_vector_schema_plan_001",
        "source_dossier_refs": [
            "WassersteinDistanceImplementationReadinessDossier.v1:"
            "wasserstein_distance_implementation_readiness_dossier_001",
        ],
        "source_metric_registry_refs": [
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
        ],
        "source_baseline_vector_pack_refs": [
            "MetricOperatorBaselineTestVectorPack.v1:"
            "metric_operator_baseline_test_vector_pack_001",
        ],
        "schema_scope": {
            "schema_family": "MIXED_SCHEMA_PLAN",
            "intended_lane": "SHADOW",
            "schema_stage": "SCHEMA_PLAN_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "P45_WASSERSTEIN_TEST_VECTOR_SCHEMA_PLAN",
            "evidence_refs": [
                "WassersteinDistanceImplementationReadinessDossier.v1:"
                "wasserstein_distance_implementation_readiness_dossier_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_test_vector_schema_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_test_vector_schema_plan(_payload())
    b = build_wasserstein_test_vector_schema_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_test_vector_schema_plan(a) == (
        serialize_wasserstein_test_vector_schema_plan(b)
    )


def test_default_groups_deterministic() -> None:
    assert default_valid_schema_groups() == default_valid_schema_groups()
    assert default_invalid_schema_groups() == default_invalid_schema_groups()
    assert default_not_computable_schema_groups() == default_not_computable_schema_groups()


def test_constants_are_enforced() -> None:
    packet = build_wasserstein_test_vector_schema_plan(_payload())
    assert packet["schema_version"] == "WassersteinTestVectorSchemaPlan.v1"
    assert packet["plan_type"] == "WASSERSTEIN_TEST_VECTOR_SCHEMA_PLAN"
    assert packet["operator_id"] == "WASSERSTEIN"


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
            lambda p: p["valid_schema_groups"].append(dict(p["valid_schema_groups"][0])),
            "duplicate_group_id",
        ),
        (
            lambda p: p["valid_schema_groups"][0].__setitem__("schema_type", "BAD"),
            "unknown_schema_type",
        ),
        (
            lambda p: p["invalid_schema_groups"][0].__setitem__("invalid_reason", "BAD"),
            "unknown_invalid_reason",
        ),
        (
            lambda p: p["not_computable_schema_groups"][0].__setitem__(
                "not_computable_reason", "BAD"
            ),
            "unknown_not_computable_reason",
        ),
        (
            lambda p: p["not_computable_schema_groups"][0].__setitem__(
                "expected_state", "BAD"
            ),
            "unknown_expected_state",
        ),
        (
            lambda p: p["invalid_schema_groups"][0].__setitem__(
                "implementation_status", "BAD"
            ),
            "unknown_implementation_status",
        ),
    ],
)
def test_enum_and_duplicate_failures(mutator, err: str) -> None:
    p = _payload()
    p["valid_schema_groups"] = default_valid_schema_groups()
    p["invalid_schema_groups"] = default_invalid_schema_groups()
    p["not_computable_schema_groups"] = default_not_computable_schema_groups()
    mutator(p)
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_schema_plan(p)


def test_locked_maps_and_flags() -> None:
    p = _payload()
    p["schema_layout_plan"] = default_schema_layout_plan()
    p["schema_layout_plan"]["fixture_files_added"] = True
    with pytest.raises(ValueError, match="invalid_schema_layout_plan"):
        build_wasserstein_test_vector_schema_plan(p)

    p = _payload()
    p["schema_constraints"] = default_schema_constraints()
    p["schema_constraints"]["wasserstein_math_added"] = True
    with pytest.raises(ValueError, match="invalid_schema_constraints"):
        build_wasserstein_test_vector_schema_plan(p)

    p = _payload()
    p["validation_plan"] = default_validation_plan()
    p["validation_plan"]["requires_schema_validation"] = False
    with pytest.raises(ValueError, match="invalid_validation_plan"):
        build_wasserstein_test_vector_schema_plan(p)

    p = _payload()
    p["output_contract"] = default_output_contract()
    p["output_contract"]["emits_wasserstein_outputs"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_wasserstein_test_vector_schema_plan(p)

    p = _payload()
    p["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_wasserstein_test_vector_schema_plan(p)


def test_all_governance_flags_locked_false() -> None:
    packet = build_wasserstein_test_vector_schema_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert packet["governance_flags"][flag] is False, flag


def test_provenance_hash_stability_and_schema() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler metric-value schema-file"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_schema_plan(p)

    packet = build_wasserstein_test_vector_schema_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_test_vector_schema_plan_hash(
        packet
    ) == compute_wasserstein_test_vector_schema_plan_hash(altered)

    changed_payload = _payload()
    changed_payload["schema_scope"]["schema_stage"] = "SCHEMA_LAYOUT_ONLY"
    changed = build_wasserstein_test_vector_schema_plan(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/wasserstein_test_vector_schema_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(packet, schema)
    assert all(
        isinstance(x, str) and x for x in packet["provenance"]["evidence_refs"]
    )


def test_output_contract_emits_schema_plan_true() -> None:
    packet = build_wasserstein_test_vector_schema_plan(_payload())
    assert packet["output_contract"]["emits_schema_plan"] is True
    assert packet["output_contract"]["emits_schema_group_metadata"] is True
    assert packet["output_contract"]["emits_metric_values"] is False
    assert packet["output_contract"]["emits_wasserstein_outputs"] is False


def test_valid_schema_groups_coverage() -> None:
    packet = build_wasserstein_test_vector_schema_plan(_payload())
    types = {g["schema_type"] for g in packet["valid_schema_groups"]}
    assert "DISTRIBUTION_PAIR_SCHEMA" in types
    assert "REFERENCE_VECTOR_SCHEMA" in types
    assert "DEGENERATE_DISTRIBUTION_SCHEMA" in types


def test_not_computable_groups_coverage() -> None:
    packet = build_wasserstein_test_vector_schema_plan(_payload())
    reasons = {g["not_computable_reason"] for g in packet["not_computable_schema_groups"]}
    assert "EMPTY_INPUT" in reasons
    assert "GROUND_METRIC_UNDECLARED" in reasons
    assert "NUMERICAL_POLICY_MISSING" in reasons


def test_invalid_groups_coverage() -> None:
    packet = build_wasserstein_test_vector_schema_plan(_payload())
    reasons = {g["invalid_reason"] for g in packet["invalid_schema_groups"]}
    assert "MISSING_REQUIRED_FIELD" in reasons
    assert "EMPTY_DISTRIBUTION" in reasons
    assert "DIMENSION_MISMATCH" in reasons


def test_source_refs_sorted() -> None:
    p = _payload()
    p["source_dossier_refs"] = ["ref_b", "ref_a"]
    packet = build_wasserstein_test_vector_schema_plan(p)
    assert packet["source_dossier_refs"] == ["ref_a", "ref_b"]


def test_blocked_operations_sorted() -> None:
    p = _payload()
    groups = default_valid_schema_groups()
    groups[0]["blocked_operations"] = ["z_op", "a_op"]
    p["valid_schema_groups"] = groups
    packet = build_wasserstein_test_vector_schema_plan(p)
    assert packet["valid_schema_groups"][0]["blocked_operations"] == ["a_op", "z_op"]


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["plan_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_schema_plan(p)
