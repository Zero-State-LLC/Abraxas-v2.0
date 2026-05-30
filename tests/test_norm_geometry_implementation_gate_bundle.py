"""Tests: NormGeometryComputationImplementationGate.v1 and NormGeometryComputationReceipt.v1."""
from __future__ import annotations

import json
import math
import pathlib

import pytest

from core.canonical.json import canonical_hash
from core.norm_geometry_computation_implementation_gate import (
    GATE_ID,
    GATE_STAGE,
    GATE_STATUS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_AUTHORIZATION_PREP_HASH,
    SOURCE_CPU_BASELINE_PLAN_HASH,
    SOURCE_OPERATOR_DECISION_HASH,
    NormGeometryComputationImplementationGateValidationError,
    build_computation_implementation_gate,
    validate_computation_implementation_gate,
)
from core.norm_geometry_computation import (
    COMPUTATION_STAGE,
    COMPUTATION_STATUS,
    RECEIPT_ID,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    NormGeometryComputationError,
    _V005_EXPECTED,
    _compute_lp_norm,
    build_computation_receipt,
    validate_computation_receipt,
)


# ── gate fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def gate() -> dict:
    return build_computation_implementation_gate()


@pytest.fixture(scope="module")
def receipt() -> dict:
    return build_computation_receipt()


# ── gate: schema and identity ─────────────────────────────────────────────────


def test_gate_schema_version(gate: dict) -> None:
    assert gate["schema_version"] == SCHEMA_VERSION


def test_gate_id(gate: dict) -> None:
    assert gate["gate_id"] == GATE_ID


def test_gate_operator_id(gate: dict) -> None:
    assert gate["operator_id"] == OPERATOR_ID


def test_gate_status(gate: dict) -> None:
    assert gate["gate_status"] == GATE_STATUS


def test_gate_stage(gate: dict) -> None:
    assert gate["gate_stage"] == GATE_STAGE


def test_gate_intended_lane_shadow(gate: dict) -> None:
    assert gate["intended_lane"] == "SHADOW"


# ── gate: source hashes ───────────────────────────────────────────────────────


def test_gate_source_cpu_baseline_plan_hash(gate: dict) -> None:
    assert gate["source_cpu_baseline_plan_hash"] == SOURCE_CPU_BASELINE_PLAN_HASH


def test_gate_source_operator_decision_hash(gate: dict) -> None:
    assert gate["source_operator_decision_hash"] == SOURCE_OPERATOR_DECISION_HASH


def test_gate_source_authorization_prep_hash(gate: dict) -> None:
    assert gate["source_authorization_prep_hash"] == SOURCE_AUTHORIZATION_PREP_HASH


# ── gate: authorized scope ────────────────────────────────────────────────────


def test_gate_authorized_computation_type(gate: dict) -> None:
    auth = gate["authorized_implementation_scope"]
    assert auth["authorized_computation_type"] == "TEST_VECTOR_COMPUTATION_ONLY"


def test_gate_authorized_lane(gate: dict) -> None:
    auth = gate["authorized_implementation_scope"]
    assert auth["authorized_lane"] == "SHADOW"


def test_gate_norm_geometry_computation_authorized(gate: dict) -> None:
    auth = gate["authorized_implementation_scope"]
    assert auth["norm_geometry_computation_implementation_authorized"] is True


def test_gate_bounded_scope_only(gate: dict) -> None:
    auth = gate["authorized_implementation_scope"]
    assert auth["bounded_scope_only"] is True


# ── gate: locked constants ────────────────────────────────────────────────────


def test_gate_locked_constants_count(gate: dict) -> None:
    lc = gate["authorized_implementation_scope"]["locked_constants_binding"]
    assert lc["constants_count"] == 5
    assert lc["all_constants_locked"] is True


def test_gate_locked_float64_declaration(gate: dict) -> None:
    lc = gate["authorized_implementation_scope"]["locked_constants_binding"]
    assert lc["float64_precision_declaration"] == "IEEE_754_BINARY64_REQUIRED"


def test_gate_locked_p_inf_sentinel(gate: dict) -> None:
    lc = gate["authorized_implementation_scope"]["locked_constants_binding"]
    assert lc["p_inf_sentinel_value_declaration"] == "STRING_INF_ONLY"


def test_gate_locked_max_element_magnitude(gate: dict) -> None:
    lc = gate["authorized_implementation_scope"]["locked_constants_binding"]
    assert lc["max_element_magnitude_declaration"] == 1_000_000.0


def test_gate_locked_max_p_value(gate: dict) -> None:
    lc = gate["authorized_implementation_scope"]["locked_constants_binding"]
    assert lc["max_p_value_declaration"] == 16.0


def test_gate_locked_nc_branches(gate: dict) -> None:
    lc = gate["authorized_implementation_scope"]["locked_constants_binding"]
    branches = set(lc["not_computable_branch_enumeration_confirmation"])
    assert branches == {
        "EMPTY_VECTOR",
        "P_PARAMETER_LT_ONE",
        "NON_FINITE_ELEMENT_VALUE",
        "MISMATCHED_VECTOR_LENGTH",
    }


# ── gate: fixture scopes ──────────────────────────────────────────────────────


def test_gate_valid_fixture_count(gate: dict) -> None:
    assert gate["valid_fixture_scope"]["fixture_count"] == 6


def test_gate_invalid_fixture_count(gate: dict) -> None:
    assert gate["rejection_fixture_scope"]["invalid_fixture_count"] == 4


def test_gate_not_computable_fixture_count(gate: dict) -> None:
    assert gate["rejection_fixture_scope"]["not_computable_fixture_count"] == 4


# ── gate: authority locks ─────────────────────────────────────────────────────


@pytest.mark.parametrize("flag", [
    "advisory_only", "shadow_lane_only", "implementation_gate_only",
    "norm_geometry_computation_implementation_authorized",
])
def test_gate_authority_locks_true(gate: dict, flag: str) -> None:
    assert gate["authority_locks"][flag] is True


@pytest.mark.parametrize("flag", [
    "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
    "production_activation", "canon_promotion", "runtime_mutation",
    "execution_authority", "inference_authority",
])
def test_gate_authority_locks_false(gate: dict, flag: str) -> None:
    assert gate["authority_locks"][flag] is False


# ── gate: blocked scopes ──────────────────────────────────────────────────────


@pytest.mark.parametrize("flag", [
    "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
    "production_activation", "canon_promotion", "runtime_mutation",
    "execution_authority", "inference_authority",
])
def test_gate_blocked_scopes_false(gate: dict, flag: str) -> None:
    assert gate["blocked_scopes"][flag] is False


# ── gate: canonical hash integrity ────────────────────────────────────────────


def test_gate_canonical_hash_length(gate: dict) -> None:
    assert isinstance(gate["canonical_hash"], str)
    assert len(gate["canonical_hash"]) == 64


def test_gate_canonical_hash_integrity(gate: dict) -> None:
    preimage = {k: v for k, v in gate.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == gate["canonical_hash"]


def test_gate_validate_passes(gate: dict) -> None:
    validate_computation_implementation_gate(gate)


# ── gate: validate rejects wrong schema_version ───────────────────────────────


def test_gate_validate_rejects_wrong_schema_version(gate: dict) -> None:
    bad = dict(gate, schema_version="wrong")
    with pytest.raises(NormGeometryComputationImplementationGateValidationError):
        validate_computation_implementation_gate(bad)


# ── gate artifact on disk ─────────────────────────────────────────────────────


def test_gate_artifact_file_present() -> None:
    p = pathlib.Path(
        "out/metric_operator/"
        "norm_geometry_computation_implementation_gate_001.latest.json"
    )
    assert p.exists(), f"gate artifact not found: {p}"


def test_gate_artifact_file_valid_json() -> None:
    p = pathlib.Path(
        "out/metric_operator/"
        "norm_geometry_computation_implementation_gate_001.latest.json"
    )
    doc = json.loads(p.read_text())
    assert doc["schema_version"] == SCHEMA_VERSION


# ── _compute_lp_norm unit tests ───────────────────────────────────────────────


def test_compute_lp_l1_exact() -> None:
    result = _compute_lp_norm([1.0, 2.0, 3.0], [4.0, 6.0, 8.0], 1.0)
    assert result == 12.0


def test_compute_lp_l2_exact() -> None:
    result = _compute_lp_norm([3.0, 4.0], [0.0, 0.0], 2.0)
    assert result == 5.0


def test_compute_lp_l_inf() -> None:
    result = _compute_lp_norm([1.0, 5.0, 2.0, 8.0], [3.0, 3.0, 6.0, 1.0], "inf")
    assert result == 7.0


def test_compute_lp_identical_zero() -> None:
    result = _compute_lp_norm([3.0, 1.0, 4.0, 1.0], [3.0, 1.0, 4.0, 1.0], 2.0)
    assert result == 0.0


def test_compute_lp_single_element() -> None:
    result = _compute_lp_norm([5.0], [2.0], 2.0)
    assert result == 3.0


def test_compute_lp_p3_deterministic() -> None:
    r1 = _compute_lp_norm(_V005_EXPECTED and [3.0, 4.0, 5.0, 0.0, 0.0], [0.0]*5, 3.0)
    r2 = _compute_lp_norm([3.0, 4.0, 5.0, 0.0, 0.0], [0.0]*5, 3.0)
    assert r1 == r2


def test_compute_lp_p3_matches_expected() -> None:
    computed = _compute_lp_norm([3.0, 4.0, 5.0, 0.0, 0.0], [0.0]*5, 3.0)
    assert computed == _V005_EXPECTED


def test_compute_lp_result_finite() -> None:
    result = _compute_lp_norm([1.0, 2.0], [3.0, 4.0], 2.0)
    assert math.isfinite(result)


def test_compute_lp_result_non_negative() -> None:
    result = _compute_lp_norm([1.0, 2.0], [3.0, 4.0], 2.0)
    assert result >= 0.0


# ── receipt: schema and identity ──────────────────────────────────────────────


def test_receipt_schema_version(receipt: dict) -> None:
    assert receipt["schema_version"] == "NormGeometryComputationReceipt.v1"


def test_receipt_id(receipt: dict) -> None:
    assert receipt["receipt_id"] == RECEIPT_ID


def test_receipt_operator_id(receipt: dict) -> None:
    assert receipt["operator_id"] == OPERATOR_ID


def test_receipt_computation_status(receipt: dict) -> None:
    assert receipt["computation_status"] == COMPUTATION_STATUS


def test_receipt_computation_stage(receipt: dict) -> None:
    assert receipt["computation_stage"] == COMPUTATION_STAGE


def test_receipt_intended_lane(receipt: dict) -> None:
    assert receipt["intended_lane"] == "SHADOW"


def test_receipt_source_gate_hash(receipt: dict) -> None:
    assert receipt["source_implementation_gate_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH


# ── receipt: valid fixture results ────────────────────────────────────────────


def test_receipt_valid_fixture_count(receipt: dict) -> None:
    assert len(receipt["valid_fixture_results"]) == 6


def test_receipt_all_valid_match(receipt: dict) -> None:
    for r in receipt["valid_fixture_results"]:
        assert r["comparison_outcome"] == "MATCH", (
            f"{r['fixture_id']} comparison_outcome={r['comparison_outcome']!r}"
        )


def test_receipt_valid_computation_outcome(receipt: dict) -> None:
    for r in receipt["valid_fixture_results"]:
        assert r["computation_outcome"] == "COMPUTED"


def test_receipt_valid_metric_emitted_false(receipt: dict) -> None:
    for r in receipt["valid_fixture_results"]:
        assert r["metric_emitted"] is False


def test_receipt_valid_l1_result(receipt: dict) -> None:
    r = next(x for x in receipt["valid_fixture_results"] if "v001" in x["fixture_id"])
    assert r["computed_lp_distance"] == 12.0


def test_receipt_valid_l2_result(receipt: dict) -> None:
    r = next(x for x in receipt["valid_fixture_results"] if "v002" in x["fixture_id"])
    assert r["computed_lp_distance"] == 5.0


def test_receipt_valid_l_inf_result(receipt: dict) -> None:
    r = next(x for x in receipt["valid_fixture_results"] if "v003" in x["fixture_id"])
    assert r["computed_lp_distance"] == 7.0


def test_receipt_valid_identical_zero(receipt: dict) -> None:
    r = next(x for x in receipt["valid_fixture_results"] if "v004" in x["fixture_id"])
    assert r["computed_lp_distance"] == 0.0


def test_receipt_valid_single_element(receipt: dict) -> None:
    r = next(x for x in receipt["valid_fixture_results"] if "v006" in x["fixture_id"])
    assert r["computed_lp_distance"] == 3.0


# ── receipt: invalid fixture results ─────────────────────────────────────────


def test_receipt_invalid_fixture_count(receipt: dict) -> None:
    assert len(receipt["invalid_fixture_results"]) == 4


def test_receipt_all_invalid_rejected(receipt: dict) -> None:
    for r in receipt["invalid_fixture_results"]:
        assert r["rejection_outcome"] == "INVALID_INPUT"


def test_receipt_invalid_computation_not_attempted(receipt: dict) -> None:
    for r in receipt["invalid_fixture_results"]:
        assert r["computation_attempted"] is False


def test_receipt_invalid_metric_emitted_false(receipt: dict) -> None:
    for r in receipt["invalid_fixture_results"]:
        assert r["metric_emitted"] is False


def test_receipt_invalid_groups_present(receipt: dict) -> None:
    groups = {r["fixture_group_id"] for r in receipt["invalid_fixture_results"]}
    assert groups == {"invalid-001", "invalid-002", "invalid-003", "invalid-004"}


# ── receipt: NOT_COMPUTABLE fixture results ───────────────────────────────────


def test_receipt_nc_fixture_count(receipt: dict) -> None:
    assert len(receipt["not_computable_fixture_results"]) == 4


def test_receipt_all_nc_outcome(receipt: dict) -> None:
    for r in receipt["not_computable_fixture_results"]:
        assert r["not_computable_outcome"] == "NOT_COMPUTABLE"


def test_receipt_nc_computation_not_attempted(receipt: dict) -> None:
    for r in receipt["not_computable_fixture_results"]:
        assert r["computation_attempted"] is False


def test_receipt_nc_metric_emitted_false(receipt: dict) -> None:
    for r in receipt["not_computable_fixture_results"]:
        assert r["metric_emitted"] is False


def test_receipt_nc_groups_present(receipt: dict) -> None:
    groups = {r["fixture_group_id"] for r in receipt["not_computable_fixture_results"]}
    assert groups == {"nc-001", "nc-002", "nc-003", "nc-004"}


def test_receipt_nc_reasons_present(receipt: dict) -> None:
    reasons = {r["not_computable_reason"] for r in receipt["not_computable_fixture_results"]}
    assert "EMPTY_VECTOR" in reasons
    assert "P_PARAMETER_LT_ONE" in reasons
    assert "NON_FINITE_ELEMENT_VALUE" in reasons
    assert "MISMATCHED_VECTOR_LENGTH" in reasons


# ── receipt: comparison summary ───────────────────────────────────────────────


def test_receipt_comparison_summary_all_match(receipt: dict) -> None:
    cs = receipt["comparison_summary"]
    assert cs["all_valid_match"] is True


def test_receipt_comparison_summary_mismatch_zero(receipt: dict) -> None:
    cs = receipt["comparison_summary"]
    assert cs["mismatch_count"] == 0


def test_receipt_comparison_summary_total(receipt: dict) -> None:
    cs = receipt["comparison_summary"]
    assert cs["total_valid_fixtures"] == 6


def test_receipt_comparison_summary_match_count(receipt: dict) -> None:
    cs = receipt["comparison_summary"]
    assert cs["match_count"] == 6


# ── receipt: locked constants enforcement ─────────────────────────────────────


def test_receipt_locked_constants_enforced(receipt: dict) -> None:
    lce = receipt["locked_constants_enforcement"]
    assert lce["all_locked_constants_enforced"] is True
    assert lce["constants_count"] == 5


def test_receipt_locked_constants_values(receipt: dict) -> None:
    lce = receipt["locked_constants_enforcement"]
    assert lce["float64_precision_declaration"] == "IEEE_754_BINARY64_REQUIRED"
    assert lce["p_inf_sentinel_value_declaration"] == "STRING_INF_ONLY"
    assert lce["max_element_magnitude_declaration"] == 1_000_000.0
    assert lce["max_p_value_declaration"] == 16.0
    nc_branches = set(lce["not_computable_branch_enumeration_confirmation"])
    assert nc_branches == {
        "EMPTY_VECTOR", "MISMATCHED_VECTOR_LENGTH",
        "NON_FINITE_ELEMENT_VALUE", "P_PARAMETER_LT_ONE",
    }


# ── receipt: authority locks ──────────────────────────────────────────────────


@pytest.mark.parametrize("flag", [
    "advisory_only", "shadow_lane_only", "test_vector_computation_only",
    "norm_geometry_computation_implementation_authorized",
])
def test_receipt_authority_locks_true(receipt: dict, flag: str) -> None:
    assert receipt["authority_locks"][flag] is True


@pytest.mark.parametrize("flag", [
    "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
    "production_activation", "canon_promotion", "runtime_mutation",
    "execution_authority", "inference_authority",
])
def test_receipt_authority_locks_false(receipt: dict, flag: str) -> None:
    assert receipt["authority_locks"][flag] is False


# ── receipt: blocked scopes ───────────────────────────────────────────────────


@pytest.mark.parametrize("flag", [
    "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
    "production_activation", "canon_promotion", "runtime_mutation",
    "execution_authority", "inference_authority",
])
def test_receipt_blocked_scopes_false(receipt: dict, flag: str) -> None:
    assert receipt["blocked_scopes"][flag] is False


# ── receipt: canonical hash integrity ─────────────────────────────────────────


def test_receipt_canonical_hash_length(receipt: dict) -> None:
    assert isinstance(receipt["canonical_hash"], str)
    assert len(receipt["canonical_hash"]) == 64


def test_receipt_canonical_hash_integrity(receipt: dict) -> None:
    preimage = {k: v for k, v in receipt.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == receipt["canonical_hash"]


def test_receipt_validate_passes(receipt: dict) -> None:
    validate_computation_receipt(receipt)


# ── receipt: validate rejects wrong schema_version ────────────────────────────


def test_receipt_validate_rejects_wrong_status(receipt: dict) -> None:
    bad = dict(receipt, computation_status="wrong")
    with pytest.raises(NormGeometryComputationError):
        validate_computation_receipt(bad)


# ── gate ↔ receipt cross-reference ───────────────────────────────────────────


def test_gate_hash_matches_receipt_source(gate: dict, receipt: dict) -> None:
    assert receipt["source_implementation_gate_hash"] == gate["canonical_hash"]
