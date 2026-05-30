from __future__ import annotations

import pytest

from core.chamfer_distance_computation_actual_pr_gate import (
    SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_FIXTURE_CREATION_GATE_HASH,
    SOURCE_OPERATOR_DECISION_HASH,
    SOURCE_OPERATOR_DECISION_ID,
    ChamferDistanceComputationActualPrGateError,
    build_chamfer_distance_computation_actual_pr_gate,
    compute_chamfer_distance_computation_actual_pr_gate_hash,
    default_authority_locks,
    default_authorized_computation_scope,
    default_authorized_fixture_manifest,
    default_blocked_scopes,
    default_computation_constraints,
    default_operator_decision_verification,
    serialize_chamfer_distance_computation_actual_pr_gate,
)


def _payload() -> dict:
    return {
        "gate_id": "chamfer_distance_computation_actual_pr_gate_001",
        "intended_lane": "SHADOW",
        "gate_stage": "COMPUTATION_ACTUAL_PR_GATE_ONLY",
        "operator_decision_verification": default_operator_decision_verification(),
        "authorized_computation_scope": default_authorized_computation_scope(),
        "authorized_fixture_manifest": default_authorized_fixture_manifest(),
        "computation_constraints": default_computation_constraints(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW",
        "provenance": {
            "source": "CHAMFER_DISTANCE_COMPUTATION_ACTUAL_PR_GATE",
            "evidence_refs": [
                f"ChamferDistanceComputationAuthorizationReview.v1:{SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH}",
            ],
            "generated_by": "PATCH_CHAMFER_DISTANCE_COMPUTATION_ACTUAL_PR_GATE_001",
            "upstream_schema_refs": [],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_build_valid_packet() -> None:
    packet = build_chamfer_distance_computation_actual_pr_gate(_payload())
    assert packet["gate_type"] == "CHAMFER_DISTANCE_COMPUTATION_ACTUAL_PR_GATE"
    assert packet["operator_id"] == "CHAMFER_DISTANCE"
    assert "canonical_hash" in packet


def test_hash_deterministic() -> None:
    p1 = build_chamfer_distance_computation_actual_pr_gate(_payload())
    p2 = build_chamfer_distance_computation_actual_pr_gate(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_hash_function() -> None:
    packet = build_chamfer_distance_computation_actual_pr_gate(_payload())
    h = compute_chamfer_distance_computation_actual_pr_gate_hash(packet)
    assert h == packet["canonical_hash"]


def test_serialize_produces_string() -> None:
    packet = build_chamfer_distance_computation_actual_pr_gate(_payload())
    s = serialize_chamfer_distance_computation_actual_pr_gate(packet)
    assert isinstance(s, str)
    assert "CHAMFER_DISTANCE_COMPUTATION_ACTUAL_PR_GATE" in s


def test_invalid_lane_raises() -> None:
    p = _payload()
    p["intended_lane"] = "PRODUCTION"
    with pytest.raises(ChamferDistanceComputationActualPrGateError):
        build_chamfer_distance_computation_actual_pr_gate(p)


def test_invalid_gate_stage_raises() -> None:
    p = _payload()
    p["gate_stage"] = "WRONG_STAGE"
    with pytest.raises(ChamferDistanceComputationActualPrGateError):
        build_chamfer_distance_computation_actual_pr_gate(p)


def test_authority_lock_violation_raises() -> None:
    p = _payload()
    al = dict(default_authority_locks())
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ChamferDistanceComputationActualPrGateError):
        build_chamfer_distance_computation_actual_pr_gate(p)


def test_forbidden_token_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime_binding_source"
    with pytest.raises(ChamferDistanceComputationActualPrGateError, match="forbidden"):
        build_chamfer_distance_computation_actual_pr_gate(p)


def test_source_constants_present() -> None:
    assert len(SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH) == 64
    assert len(SOURCE_COMPUTATION_RECEIPT_HASH) == 64
    assert len(SOURCE_OPERATOR_DECISION_HASH) == 64
    assert SOURCE_OPERATOR_DECISION_ID.startswith("CHAMFER_DISTANCE_COMPUTATION_OPERATOR")
    assert len(SOURCE_FIXTURE_CREATION_GATE_HASH) == 64


def test_authorized_scope_fixture_count() -> None:
    scope = default_authorized_computation_scope()
    assert scope["fixture_count"] == 13
    assert scope["computation_scope_status"] == "AUTHORIZED"


def test_authorized_manifest_totals() -> None:
    manifest = default_authorized_fixture_manifest()
    assert manifest["total_authorized_fixtures"] == 13
    assert manifest["valid_fixtures"] == 5


def test_computation_constraints_all_enforced() -> None:
    cc = default_computation_constraints()
    assert cc["constraints_status"] == "ALL_CONSTRAINTS_ENFORCED"
    assert cc["shadow_lane_only"] is True
    assert cc["no_metric_value_emission"] is True


def test_authority_locks_defaults() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False


def test_blocked_scopes_all_false() -> None:
    assert all(v is False for v in default_blocked_scopes().values())
