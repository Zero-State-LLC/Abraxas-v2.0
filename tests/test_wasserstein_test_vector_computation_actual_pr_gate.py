from __future__ import annotations

import pytest

from core.wasserstein_test_vector_computation_actual_pr_gate import (
    SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH,
    SOURCE_GATE_HASH,
    SOURCE_OPERATOR_DECISION_HASH,
    SOURCE_OPERATOR_DECISION_ID,
    SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH,
    build_wasserstein_test_vector_computation_actual_pr_gate,
    compute_wasserstein_test_vector_computation_actual_pr_gate_hash,
    default_authority_locks,
    default_authorized_computation_scope,
    default_authorized_fixture_manifest,
    default_blocked_scopes,
    default_computation_constraints,
    default_operator_decision_verification,
    serialize_wasserstein_test_vector_computation_actual_pr_gate,
)


def _payload() -> dict:
    return {
        "gate_id": "wasserstein_test_vector_computation_actual_pr_gate_001",
        "intended_lane": "SHADOW",
        "gate_stage": "TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE_ONLY",
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_COMPUTATION_IMPLEMENTATION"
        ),
        "provenance": {
            "source": (
                "P57_WASSERSTEIN_TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE"
            ),
            "evidence_refs": [
                "WassersteinTestVectorComputationAuthorizationReview.v1:"
                "wasserstein_test_vector_computation_authorization_review_001",
                "WassersteinComputationOperatorDecision.v1:"
                "WASSERSTEIN_COMPUTATION_OPERATOR_DECISION_2026_05_29_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_computation_actual_pr_gate"
                ".v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    b = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    b = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    assert serialize_wasserstein_test_vector_computation_actual_pr_gate(
        a
    ) == serialize_wasserstein_test_vector_computation_actual_pr_gate(b)


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorComputationActualPrGate.v1"
    )
    assert (
        packet["gate_type"]
        == "WASSERSTEIN_TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_operator_decision_id"] == SOURCE_OPERATOR_DECISION_ID
    assert packet["source_operator_decision_hash"] == SOURCE_OPERATOR_DECISION_HASH
    assert (
        packet["source_computation_authorization_review_hash"]
        == SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH
    )
    assert (
        packet["source_fixture_schema_validation_complete_review_hash"]
        == SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
    )
    assert packet["intended_lane"] == "SHADOW"
    assert packet["gate_stage"] == "TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE_ONLY"


# ---------------------------------------------------------------------------
# Authority locks — wasserstein_computation_authorized is now TRUE
# ---------------------------------------------------------------------------


def test_computation_authorized_true() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    assert packet["authority_locks"]["wasserstein_computation_authorized"] is True


def test_gate_only_lock_true() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    assert (
        packet["authority_locks"]["test_vector_computation_actual_pr_gate_only"]
        is True
    )


def test_computation_authorized_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["wasserstein_computation_authorized"] = False
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="wasserstein_computation_authorized_must_be_true"
    ):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_gate_only_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["test_vector_computation_actual_pr_gate_only"] = False
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="test_vector_computation_actual_pr_gate_only_must_be_true"
    ):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["advisory_only"] = False
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_execution_authority_false() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    assert packet["authority_locks"]["execution_authority"] is False


def test_emits_metric_values_false() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    assert packet["authority_locks"]["emits_metric_values"] is False


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["emits_metric_values"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Operator decision verification
# ---------------------------------------------------------------------------


def test_operator_decision_verification_fields() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    odv = packet["operator_decision_verification"]
    assert odv["operator_decision_id"] == SOURCE_OPERATOR_DECISION_ID
    assert odv["operator_decision_hash"] == SOURCE_OPERATOR_DECISION_HASH
    assert odv["verification_status"] == "VERIFIED"
    assert (
        odv["upstream_review_hash_verified"]
        == SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH
    )


def test_operator_decision_id_mismatch_raises() -> None:
    p = _payload()
    odv = default_operator_decision_verification()
    odv["operator_decision_id"] = "WRONG_ID"
    p["operator_decision_verification"] = odv
    with pytest.raises(ValueError, match="operator_decision_id_mismatch"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_operator_decision_hash_mismatch_raises() -> None:
    p = _payload()
    odv = default_operator_decision_verification()
    odv["operator_decision_hash"] = "0" * 64
    p["operator_decision_verification"] = odv
    with pytest.raises(ValueError, match="operator_decision_hash_mismatch"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_operator_decision_not_verified_raises() -> None:
    p = _payload()
    odv = default_operator_decision_verification()
    odv["verification_status"] = "PENDING"
    p["operator_decision_verification"] = odv
    with pytest.raises(ValueError, match="operator_decision_not_verified"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_operator_decision_mutation_raises() -> None:
    p = _payload()
    odv = default_operator_decision_verification()
    odv["operator_id_verified"] = "WRONG"
    p["operator_decision_verification"] = odv
    with pytest.raises(ValueError, match="invalid_operator_decision_verification"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Authorized computation scope
# ---------------------------------------------------------------------------


def test_authorized_computation_scope() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    acs = packet["authorized_computation_scope"]
    assert acs["computation_scope_status"] == "AUTHORIZED"
    assert acs["fixture_count"] == 14
    assert "SHADOW" in acs["authorized_lanes"]
    assert acs["no_forecast_influence"] is True
    assert acs["no_runtime_binding"] is True
    assert acs["no_p43_surface_lane_output"] is True
    assert acs["no_production_activation"] is True


def test_scope_not_authorized_raises() -> None:
    p = _payload()
    acs = default_authorized_computation_scope()
    acs["computation_scope_status"] = "BLOCKED"
    p["authorized_computation_scope"] = acs
    with pytest.raises(ValueError, match="computation_scope_not_authorized"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_scope_fixture_count_mismatch_raises() -> None:
    p = _payload()
    acs = default_authorized_computation_scope()
    acs["fixture_count"] = 10
    p["authorized_computation_scope"] = acs
    with pytest.raises(ValueError, match="computation_scope_fixture_count_mismatch"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_scope_mutation_raises() -> None:
    p = _payload()
    acs = default_authorized_computation_scope()
    acs["no_production_activation"] = False
    p["authorized_computation_scope"] = acs
    with pytest.raises(ValueError, match="invalid_authorized_computation_scope"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Authorized fixture manifest
# ---------------------------------------------------------------------------


def test_authorized_fixture_manifest() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    afm = packet["authorized_fixture_manifest"]
    assert afm["total_authorized_fixtures"] == 14
    assert afm["source_gate_hash"] == SOURCE_GATE_HASH
    assert afm["manifest_status"] == "AUTHORIZED_FOR_BOUNDED_COMPUTATION"


def test_manifest_count_mismatch_raises() -> None:
    p = _payload()
    afm = default_authorized_fixture_manifest()
    afm["total_authorized_fixtures"] = 12
    p["authorized_fixture_manifest"] = afm
    with pytest.raises(ValueError, match="authorized_fixture_count_mismatch"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_manifest_gate_hash_mismatch_raises() -> None:
    p = _payload()
    afm = default_authorized_fixture_manifest()
    afm["source_gate_hash"] = "0" * 64
    p["authorized_fixture_manifest"] = afm
    with pytest.raises(ValueError, match="authorized_fixture_gate_hash_mismatch"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_manifest_mutation_raises() -> None:
    p = _payload()
    afm = default_authorized_fixture_manifest()
    afm["manifest_status"] = "BLOCKED"
    p["authorized_fixture_manifest"] = afm
    with pytest.raises(ValueError, match="authorized_fixture_manifest_not_ready"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Computation constraints
# ---------------------------------------------------------------------------


def test_computation_constraints() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    cc = packet["computation_constraints"]
    assert cc["bounded_to_validated_fixtures_only"] is True
    assert cc["shadow_lane_only"] is True
    assert cc["no_metric_value_emission"] is True
    assert cc["no_expected_distance_addition"] is True
    assert cc["no_p43_surface_lanes"] is True
    assert cc["no_production_activation"] is True
    assert cc["no_canon_promotion"] is True
    assert cc["no_runtime_mutation"] is True
    assert cc["no_execution_authority"] is True
    assert cc["no_inference_authority"] is True
    assert cc["constraint_status"] == "ACTIVE"


def test_not_bounded_raises() -> None:
    p = _payload()
    cc = default_computation_constraints()
    cc["bounded_to_validated_fixtures_only"] = False
    p["computation_constraints"] = cc
    with pytest.raises(ValueError, match="computation_not_bounded_to_fixtures"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_metric_emission_not_blocked_raises() -> None:
    p = _payload()
    cc = default_computation_constraints()
    cc["no_metric_value_emission"] = False
    p["computation_constraints"] = cc
    with pytest.raises(ValueError, match="metric_value_emission_not_blocked"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_constraints_mutation_raises() -> None:
    p = _payload()
    cc = default_computation_constraints()
    cc["no_production_activation"] = False
    p["computation_constraints"] = cc
    with pytest.raises(ValueError, match="invalid_computation_constraints"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_test_vector_computation_actual_pr_gate_hash(packet)
        == compute_wasserstein_test_vector_computation_actual_pr_gate_hash(altered)
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_computation_actual_pr_gate(_payload())
    b = build_wasserstein_test_vector_computation_actual_pr_gate(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["gate_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("gate_stage", "ACTIVE", "unknown_gate_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_computation_actual_pr_gate(p)
