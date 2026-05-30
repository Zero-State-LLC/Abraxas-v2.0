"""Tests for WassersteinCpuBaselineImplementationGate.v1."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.wasserstein_cpu_baseline_implementation_gate import (
    EXPECTED_NOT_COMPUTABLE_BRANCHES,
    EXPECTED_SOLVER_POLICY,
    EXPECTED_FIXTURE_SCOPE,
    EXPECTED_FLOAT64_DECLARATION,
    GATE_ID,
    GATE_STAGE,
    GATE_STATUS,
    OPERATOR_ID,
    REQUIRED_LOCKED_CONSTANT_KEYS,
    SCHEMA_VERSION,
    SOURCE_OPERATOR_DECISION_HASH,
    WassersteinCpuBaselineImplementationGateValidationError,
    build_authority_locks,
    build_blocked_scopes,
    build_authorized_implementation_scope,
    build_no_metric_emission_block,
    build_no_forecast_influence_block,
    build_no_p43_surface_lane_block,
    build_wasserstein_cpu_baseline_implementation_gate,
    validate_wasserstein_cpu_baseline_implementation_gate,
)
from core.canonical.json import canonical_hash


# ── constant invariants ────────────────────────────────────────────────────────

def test_schema_version_constant() -> None:
    assert SCHEMA_VERSION == "WassersteinCpuBaselineImplementationGate.v1"


def test_gate_status_constant() -> None:
    assert GATE_STATUS == "WASSERSTEIN_CPU_BASELINE_IMPLEMENTATION_GATE_READY"


def test_gate_stage_constant() -> None:
    assert GATE_STAGE == "COMPUTATION_IMPLEMENTATION_GATE_ONLY"


def test_operator_id_wasserstein() -> None:
    assert OPERATOR_ID == "WASSERSTEIN"


def test_gate_id() -> None:
    assert GATE_ID == "wasserstein_cpu_baseline_implementation_gate_001"


def test_seven_locked_constant_keys() -> None:
    assert len(REQUIRED_LOCKED_CONSTANT_KEYS) == 7


def test_seven_not_computable_branches() -> None:
    assert len(EXPECTED_NOT_COMPUTABLE_BRANCHES) == 7


def test_source_operator_decision_hash_64_chars() -> None:
    assert len(SOURCE_OPERATOR_DECISION_HASH) == 64
    assert all(c in "0123456789abcdef" for c in SOURCE_OPERATOR_DECISION_HASH)


def test_expected_operator_decision_hash_matches_artifact() -> None:
    from core.canonical.json import canonical_hash
    doc = json.loads(
        Path("input/wasserstein_cpu_baseline_implementation_authorization_operator_decision.json").read_text()
    )
    assert canonical_hash(doc) == SOURCE_OPERATOR_DECISION_HASH


def test_solver_policy_constant() -> None:
    assert EXPECTED_SOLVER_POLICY == "DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY"


def test_fixture_scope_constant() -> None:
    assert EXPECTED_FIXTURE_SCOPE == "EXISTING_WASSERSTEIN_TEST_VECTOR_FIXTURES_ONLY"


def test_float64_declaration_constant() -> None:
    assert EXPECTED_FLOAT64_DECLARATION == "IEEE_754_BINARY64_REQUIRED"


def test_not_computable_branches_content() -> None:
    expected = {
        "EMPTY_DISTRIBUTION",
        "UNBALANCED_MASS",
        "NEGATIVE_MASS",
        "NON_FINITE_WEIGHT",
        "NON_FINITE_COORDINATE",
        "MISSING_REQUIRED_FIELD",
        "MISMATCHED_SUPPORT_WEIGHT_LENGTH",
    }
    assert EXPECTED_NOT_COMPUTABLE_BRANCHES == expected


def test_required_locked_constant_keys_content() -> None:
    expected = {
        "solver_policy",
        "supported_fixture_scope",
        "float64_precision_declaration",
        "balance_tolerance_declaration",
        "max_distribution_length_declaration",
        "max_coordinate_magnitude_declaration",
        "not_computable_branch_enumeration_confirmation",
    }
    assert set(REQUIRED_LOCKED_CONSTANT_KEYS) == expected


# ── builder helpers ────────────────────────────────────────────────────────────

def test_authority_locks_true_flags() -> None:
    locks = build_authority_locks()
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["implementation_gate_only"] is True
    assert locks["wasserstein_cpu_baseline_implementation_authorized"] is True


def test_authority_locks_false_flags() -> None:
    locks = build_authority_locks()
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        assert locks[flag] is False, f"authority_locks.{flag} must be False"


def test_blocked_scopes_all_false() -> None:
    blocked = build_blocked_scopes()
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        assert blocked[flag] is False, f"blocked_scopes.{flag} must be False"


def test_no_metric_emission_block_structure() -> None:
    block = build_no_metric_emission_block()
    assert block["emits_metric_values"] is False
    assert block["metric_emission_blocked"] is True
    assert block["block_confirmed"] is True


def test_no_forecast_influence_block_structure() -> None:
    block = build_no_forecast_influence_block()
    assert block["forecast_influence"] is False
    assert block["forecast_influence_blocked"] is True
    assert block["block_confirmed"] is True


def test_no_p43_surface_lane_block_structure() -> None:
    block = build_no_p43_surface_lane_block()
    assert block["p43_surface_lanes_authorized"] is False
    assert block["p43_blocked"] is True
    assert block["block_confirmed"] is True


def test_authorized_implementation_scope_structure() -> None:
    lc = {"all_constants_locked": True, "constants_count": 7}
    scope = build_authorized_implementation_scope(lc)
    assert scope["wasserstein_cpu_baseline_implementation_authorized"] is True
    assert scope["authorized_computation_type"] == "TEST_VECTOR_COMPUTATION_ONLY"
    assert scope["bounded_scope_only"] is True
    assert scope["fixture_scope"] == EXPECTED_FIXTURE_SCOPE
    assert scope["locked_constants_binding"] is lc


# ── full build ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def gate() -> dict:
    return build_wasserstein_cpu_baseline_implementation_gate()


def test_gate_schema_version(gate: dict) -> None:
    assert gate["schema_version"] == SCHEMA_VERSION


def test_gate_status(gate: dict) -> None:
    assert gate["gate_status"] == GATE_STATUS


def test_gate_stage(gate: dict) -> None:
    assert gate["gate_stage"] == GATE_STAGE


def test_gate_operator_id(gate: dict) -> None:
    assert gate["operator_id"] == OPERATOR_ID


def test_gate_id_field(gate: dict) -> None:
    assert gate["gate_id"] == GATE_ID


def test_gate_intended_lane_shadow(gate: dict) -> None:
    assert gate["intended_lane"] == "SHADOW"


def test_gate_source_operator_decision_hash(gate: dict) -> None:
    assert gate["source_operator_decision_hash"] == SOURCE_OPERATOR_DECISION_HASH


def test_gate_locked_constants_all_locked(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    assert lc["all_constants_locked"] is True


def test_gate_locked_constants_count(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    assert lc["constants_count"] == 7


def test_gate_locked_constants_solver_policy(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    assert lc["solver_policy"] == EXPECTED_SOLVER_POLICY


def test_gate_locked_constants_fixture_scope(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    assert lc["supported_fixture_scope"] == EXPECTED_FIXTURE_SCOPE


def test_gate_locked_constants_float64(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    assert lc["float64_precision_declaration"] == EXPECTED_FLOAT64_DECLARATION


def test_gate_locked_constants_balance_tolerance(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    bt = lc["balance_tolerance_declaration"]
    assert "epsilon_rel" in bt
    assert "epsilon_abs" in bt
    assert isinstance(bt["epsilon_rel"], float)
    assert isinstance(bt["epsilon_abs"], float)


def test_gate_locked_constants_max_distribution_length(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    assert lc["max_distribution_length_declaration"] == 16


def test_gate_locked_constants_max_coordinate_magnitude(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    assert lc["max_coordinate_magnitude_declaration"] == 1_000_000.0


def test_gate_locked_constants_nc_branches(gate: dict) -> None:
    lc = gate["locked_constants_binding"]
    nc = set(lc["not_computable_branch_enumeration_confirmation"])
    assert nc == EXPECTED_NOT_COMPUTABLE_BRANCHES


def test_gate_fixture_scope_review_confirmed(gate: dict) -> None:
    fsr = gate["fixture_scope_review"]
    assert fsr["fixture_scope_confirmed"] is True


def test_gate_fixture_scope_review_not_yet_executed(gate: dict) -> None:
    fsr = gate["fixture_scope_review"]
    assert fsr["computation_implementation_not_yet_executed"] is True


def test_gate_fixture_scope_valid_count(gate: dict) -> None:
    fsr = gate["fixture_scope_review"]
    assert fsr["valid_fixture_count"] == 5


def test_gate_fixture_scope_invalid_count(gate: dict) -> None:
    fsr = gate["fixture_scope_review"]
    assert fsr["invalid_fixture_count"] == 5


def test_gate_fixture_scope_nc_count(gate: dict) -> None:
    fsr = gate["fixture_scope_review"]
    assert fsr["not_computable_fixture_count"] == 4


def test_gate_fixture_scope_total_count(gate: dict) -> None:
    fsr = gate["fixture_scope_review"]
    assert fsr["total_fixture_count"] == 14


def test_gate_authority_locks_true_flags(gate: dict) -> None:
    locks = gate["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["implementation_gate_only"] is True
    assert locks["wasserstein_cpu_baseline_implementation_authorized"] is True


def test_gate_authority_locks_false_flags(gate: dict) -> None:
    locks = gate["authority_locks"]
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        assert locks[flag] is False, f"authority_locks.{flag} must be False"


def test_gate_blocked_scopes_all_false(gate: dict) -> None:
    blocked = gate["blocked_scopes"]
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        assert blocked[flag] is False, f"blocked_scopes.{flag} must be False"


def test_gate_authorized_scope_authorized(gate: dict) -> None:
    auth = gate["authorized_implementation_scope"]
    assert auth["wasserstein_cpu_baseline_implementation_authorized"] is True
    assert auth["authorized_computation_type"] == "TEST_VECTOR_COMPUTATION_ONLY"
    assert auth["bounded_scope_only"] is True


def test_gate_canonical_hash_present(gate: dict) -> None:
    h = gate["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_gate_canonical_hash_valid(gate: dict) -> None:
    preimage = {k: v for k, v in gate.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == gate["canonical_hash"]


def test_gate_recommended_next_step(gate: dict) -> None:
    assert gate["recommended_next_step"] == (
        "WASSERSTEIN_IMPLEMENTATION_AUTHORIZED_BOUNDED_SHADOW_COMPUTATION_PR"
    )


def test_gate_no_metric_emission_block(gate: dict) -> None:
    block = gate["no_metric_emission_block"]
    assert block["emits_metric_values"] is False
    assert block["block_confirmed"] is True


def test_gate_no_forecast_influence_block(gate: dict) -> None:
    block = gate["no_forecast_influence_block"]
    assert block["forecast_influence"] is False
    assert block["block_confirmed"] is True


def test_gate_no_p43_block(gate: dict) -> None:
    block = gate["no_p43_surface_lane_block"]
    assert block["p43_surface_lanes_authorized"] is False
    assert block["block_confirmed"] is True


# ── validate function ──────────────────────────────────────────────────────────

def test_validate_passes_on_valid_gate(gate: dict) -> None:
    validate_wasserstein_cpu_baseline_implementation_gate(gate)


def test_validate_rejects_wrong_schema_version(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["schema_version"] = "Wrong.v1"
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_wrong_gate_status(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["gate_status"] = "WRONG"
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_wrong_operator_id(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["operator_id"] = "TRANSPORT"
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_wrong_decision_hash(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["source_operator_decision_hash"] = "a" * 64
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_emits_metric_values_true(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["authority_locks"]["emits_metric_values"] = True
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_advisory_only_false(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["authority_locks"]["advisory_only"] = False
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_constants_count_not_7(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["authorized_implementation_scope"]["locked_constants_binding"]["constants_count"] = 6
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_wrong_nc_branches(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["authorized_implementation_scope"]["locked_constants_binding"][
        "not_computable_branch_enumeration_confirmation"
    ] = ["WRONG_BRANCH"]
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_tampered_canonical_hash(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["canonical_hash"] = "b" * 64
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_fixture_scope_not_confirmed(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["fixture_scope_review"]["fixture_scope_confirmed"] = False
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)


def test_validate_rejects_computation_already_executed(gate: dict) -> None:
    bad = copy.deepcopy(gate)
    bad["fixture_scope_review"]["computation_implementation_not_yet_executed"] = False
    bad["canonical_hash"] = canonical_hash({k: v for k, v in bad.items() if k != "canonical_hash"})
    with pytest.raises(WassersteinCpuBaselineImplementationGateValidationError):
        validate_wasserstein_cpu_baseline_implementation_gate(bad)
