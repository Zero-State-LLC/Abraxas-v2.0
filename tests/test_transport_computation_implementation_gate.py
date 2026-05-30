from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.transport_computation_implementation_gate import (
    GATE_STATUS,
    GATE_STAGE,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_DECISION_RECORD_HASH,
    SOURCE_OPERATOR_DECISION_HASH,
    EXPECTED_NOT_COMPUTABLE_BRANCHES,
    REQUIRED_LOCKED_CONSTANT_KEYS,
    TransportComputationImplementationGateValidationError,
    build_authority_locks,
    build_blocked_scopes,
    build_authorized_implementation_scope,
    build_no_metric_emission_block,
    build_no_forecast_influence_block,
    build_no_p43_surface_lane_block,
    build_transport_computation_implementation_gate,
    validate_transport_computation_implementation_gate,
    _build_locked_constants_binding,
)
from core.canonical.json import canonical_hash

_VALID_LOCKED_CONSTANTS_RECORD = {
    "lp_solver_variant_declaration": "DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH",
    "pivot_rule_declaration": "LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR",
    "tie_breaking_rule_declaration": "ROW_MAJOR_THEN_COLUMN_MAJOR",
    "balance_tolerance_declaration": {"epsilon_rel": 1e-9, "epsilon_abs": 1e-12},
    "max_problem_size_declaration": {
        "max_supply_length": 4,
        "max_demand_length": 4,
        "max_transport_variables": 16,
    },
    "cost_matrix_magnitude_bound_declaration": 1000000.0,
    "not_computable_branch_enumeration_confirmation": sorted(
        EXPECTED_NOT_COMPUTABLE_BRANCHES
    ),
    "all_locked_constants_present": True,
    "constants_valid_for_test_vector_scope": True,
}

_VALID_DECISION_RECORD = {
    "schema_version": "TransportImplementationAuthorizationDecisionRecord.v1",
    "record_id": "transport_implementation_authorization_decision_record_001",
    "operator_id": "TRANSPORT",
    "source_operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
    "record_status": "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORDED",
    "implementation_lane_authorized": "TEST_VECTOR_COMPUTATION_ONLY",
    "baseline_target": "SHADOW_STUB_ONLY",
    "locked_constants_record": _VALID_LOCKED_CONSTANTS_RECORD,
    "decision_validation_review": {"decision_valid": True},
    "blocked_scope_acknowledgement_review": {"all_acknowledgements_confirmed": True},
    "canonical_hash": SOURCE_DECISION_RECORD_HASH,
}


# ── constant invariants ────────────────────────────────────────────────────────

def test_schema_version_constant() -> None:
    assert SCHEMA_VERSION == "TransportComputationImplementationGate.v1"


def test_gate_status_constant() -> None:
    assert GATE_STATUS == "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE_READY"


def test_gate_stage_constant() -> None:
    assert GATE_STAGE == "COMPUTATION_IMPLEMENTATION_GATE_ONLY"


def test_operator_id_transport() -> None:
    assert OPERATOR_ID == "TRANSPORT"


def test_seven_locked_constant_keys() -> None:
    assert len(REQUIRED_LOCKED_CONSTANT_KEYS) == 7


def test_nine_not_computable_branches() -> None:
    assert len(EXPECTED_NOT_COMPUTABLE_BRANCHES) == 9


def test_source_decision_record_hash_64_chars() -> None:
    assert len(SOURCE_DECISION_RECORD_HASH) == 64
    assert all(c in "0123456789abcdef" for c in SOURCE_DECISION_RECORD_HASH)


def test_source_operator_decision_hash_64_chars() -> None:
    assert len(SOURCE_OPERATOR_DECISION_HASH) == 64
    assert all(c in "0123456789abcdef" for c in SOURCE_OPERATOR_DECISION_HASH)


def test_expected_decision_record_hash_matches_artifact() -> None:
    artifact = Path(
        "out/metric_operator/"
        "transport_implementation_authorization_decision_record_001.latest.json"
    )
    if not artifact.exists():
        pytest.skip("decision record artifact not present")
    data = json.loads(artifact.read_text())
    assert data["canonical_hash"] == SOURCE_DECISION_RECORD_HASH


# ── _build_locked_constants_binding ───────────────────────────────────────────

def test_locked_constants_binding_all_present() -> None:
    lcb = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    assert lcb["all_constants_locked"] is True


def test_locked_constants_binding_count_seven() -> None:
    lcb = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    assert lcb["constants_count"] == 7


def test_locked_constants_binding_solver_variant() -> None:
    lcb = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    assert lcb["lp_solver_variant_declaration"] == (
        "DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH"
    )


def test_locked_constants_binding_pivot_rule() -> None:
    lcb = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    assert lcb["pivot_rule_declaration"] == "LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR"


def test_locked_constants_binding_tie_breaking() -> None:
    lcb = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    assert lcb["tie_breaking_rule_declaration"] == "ROW_MAJOR_THEN_COLUMN_MAJOR"


def test_locked_constants_binding_max_problem_size() -> None:
    lcb = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    mps = lcb["max_problem_size_declaration"]
    assert mps["max_supply_length"] == 4
    assert mps["max_demand_length"] == 4
    assert mps["max_transport_variables"] == 16


def test_locked_constants_binding_cost_matrix_bound() -> None:
    lcb = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    assert lcb["cost_matrix_magnitude_bound_declaration"] == 1000000.0


def test_locked_constants_binding_nc_branches_sorted() -> None:
    lcb = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    branches = lcb["not_computable_branch_enumeration_confirmation"]
    assert branches == sorted(branches)
    assert set(branches) == EXPECTED_NOT_COMPUTABLE_BRANCHES


# ── build_authorized_implementation_scope ─────────────────────────────────────

def test_authorized_scope_transport_authorized() -> None:
    lc = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    scope = build_authorized_implementation_scope(lc)
    assert scope["transport_computation_implementation_authorized"] is True


def test_authorized_scope_lp_solver_authorized() -> None:
    lc = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    scope = build_authorized_implementation_scope(lc)
    assert scope["lp_solver_invocation_authorized_for_test_vectors"] is True


def test_authorized_scope_computation_type() -> None:
    lc = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    scope = build_authorized_implementation_scope(lc)
    assert scope["authorized_computation_type"] == "TEST_VECTOR_COMPUTATION_ONLY"


def test_authorized_scope_bounded_only() -> None:
    lc = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    scope = build_authorized_implementation_scope(lc)
    assert scope["bounded_scope_only"] is True


def test_authorized_scope_algorithm() -> None:
    lc = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    scope = build_authorized_implementation_scope(lc)
    assert scope["authorized_algorithm"] == "DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH"


def test_authorized_scope_lane_shadow() -> None:
    lc = _build_locked_constants_binding(_VALID_DECISION_RECORD)
    scope = build_authorized_implementation_scope(lc)
    assert scope["authorized_lane"] == "SHADOW"


# ── build_authority_locks ──────────────────────────────────────────────────────

def test_authority_locks_advisory_true() -> None:
    locks = build_authority_locks()
    assert locks["advisory_only"] is True


def test_authority_locks_shadow_lane_only_true() -> None:
    locks = build_authority_locks()
    assert locks["shadow_lane_only"] is True


def test_authority_locks_implementation_gate_only_true() -> None:
    locks = build_authority_locks()
    assert locks["implementation_gate_only"] is True


def test_authority_locks_transport_authorized_true() -> None:
    locks = build_authority_locks()
    assert locks["transport_computation_implementation_authorized"] is True


def test_authority_locks_lp_solver_authorized_true() -> None:
    locks = build_authority_locks()
    assert locks["lp_solver_invocation_authorized_for_test_vectors"] is True


def test_authority_locks_all_blocking_false() -> None:
    locks = build_authority_locks()
    for key in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert locks[key] is False, f"authority_locks.{key} must be False"


# ── build_blocked_scopes ───────────────────────────────────────────────────────

def test_blocked_scopes_all_false() -> None:
    bs = build_blocked_scopes()
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


def test_blocked_scopes_eight_keys() -> None:
    assert len(build_blocked_scopes()) == 8


# ── block confirmations ────────────────────────────────────────────────────────

def test_no_metric_emission_block() -> None:
    b = build_no_metric_emission_block()
    assert b["emits_metric_values"] is False
    assert b["block_confirmed"] is True
    assert b["metric_emission_blocked"] is True


def test_no_forecast_influence_block() -> None:
    b = build_no_forecast_influence_block()
    assert b["forecast_influence"] is False
    assert b["block_confirmed"] is True
    assert b["forecast_influence_blocked"] is True


def test_no_p43_surface_lane_block() -> None:
    b = build_no_p43_surface_lane_block()
    assert b["p43_surface_lanes_authorized"] is False
    assert b["block_confirmed"] is True
    assert b["p43_blocked"] is True


# ── full build (reads disk artifacts) ─────────────────────────────────────────

def test_gate_builds_successfully() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["gate_status"] == GATE_STATUS


def test_gate_schema_version() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["schema_version"] == SCHEMA_VERSION


def test_gate_operator_id() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["operator_id"] == "TRANSPORT"


def test_gate_stage() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["gate_stage"] == GATE_STAGE


def test_gate_source_decision_record_hash() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["source_decision_record_hash"] == SOURCE_DECISION_RECORD_HASH


def test_gate_source_operator_decision_hash() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["source_operator_decision_hash"] == SOURCE_OPERATOR_DECISION_HASH


def test_gate_transport_implementation_authorized() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["authority_locks"]["transport_computation_implementation_authorized"] is True


def test_gate_lp_solver_authorized_for_test_vectors() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["authority_locks"]["lp_solver_invocation_authorized_for_test_vectors"] is True


def test_gate_advisory_only() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["authority_locks"]["advisory_only"] is True


def test_gate_shadow_lane_only() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["authority_locks"]["shadow_lane_only"] is True


def test_gate_implementation_gate_only() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["authority_locks"]["implementation_gate_only"] is True


def test_gate_all_blocking_locks_false() -> None:
    gate = build_transport_computation_implementation_gate()
    locks = gate["authority_locks"]
    for key in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert locks[key] is False, f"authority_locks.{key} must be False"


def test_gate_locked_constants_count_seven() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["locked_constants_binding"]["constants_count"] == 7


def test_gate_locked_constants_all_locked() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["locked_constants_binding"]["all_constants_locked"] is True


def test_gate_nc_branches_nine() -> None:
    gate = build_transport_computation_implementation_gate()
    branches = gate["locked_constants_binding"][
        "not_computable_branch_enumeration_confirmation"
    ]
    assert len(branches) == 9
    assert set(branches) == EXPECTED_NOT_COMPUTABLE_BRANCHES


def test_gate_blocked_scopes_all_false() -> None:
    gate = build_transport_computation_implementation_gate()
    for key, val in gate["blocked_scopes"].items():
        assert val is False, f"blocked_scopes.{key} must be False"


def test_gate_no_metric_emission_block_confirmed() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["no_metric_emission_block"]["emits_metric_values"] is False
    assert gate["no_metric_emission_block"]["block_confirmed"] is True


def test_gate_no_forecast_influence_block_confirmed() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["no_forecast_influence_block"]["forecast_influence"] is False
    assert gate["no_forecast_influence_block"]["block_confirmed"] is True


def test_gate_no_p43_block_confirmed() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["no_p43_surface_lane_block"]["p43_surface_lanes_authorized"] is False
    assert gate["no_p43_surface_lane_block"]["block_confirmed"] is True


def test_gate_recommended_next_step() -> None:
    gate = build_transport_computation_implementation_gate()
    assert gate["recommended_next_step"] == (
        "TRANSPORT_IMPLEMENTATION_AUTHORIZED_BOUNDED_SHADOW_COMPUTATION_PR"
    )


def test_gate_canonical_hash_64_chars() -> None:
    gate = build_transport_computation_implementation_gate()
    h = gate["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_gate_canonical_hash_recomputable() -> None:
    gate = build_transport_computation_implementation_gate()
    preimage = {k: v for k, v in gate.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == gate["canonical_hash"]


def test_gate_deterministic() -> None:
    a = build_transport_computation_implementation_gate()
    b = build_transport_computation_implementation_gate()
    assert a["canonical_hash"] == b["canonical_hash"]


# ── validate_transport_computation_implementation_gate ────────────────────────

def test_validate_passes_on_valid_gate() -> None:
    gate = build_transport_computation_implementation_gate()
    validate_transport_computation_implementation_gate(gate)


def test_validate_wrong_schema_version_raises() -> None:
    gate = build_transport_computation_implementation_gate()
    bad = {**gate, "schema_version": "Wrong.v1"}
    with pytest.raises(TransportComputationImplementationGateValidationError):
        validate_transport_computation_implementation_gate(bad)


def test_validate_wrong_gate_status_raises() -> None:
    gate = build_transport_computation_implementation_gate()
    bad = {**gate, "gate_status": "WRONG"}
    with pytest.raises(TransportComputationImplementationGateValidationError):
        validate_transport_computation_implementation_gate(bad)


def test_validate_wrong_source_decision_hash_raises() -> None:
    gate = build_transport_computation_implementation_gate()
    bad = {**gate, "source_decision_record_hash": "a" * 64}
    with pytest.raises(TransportComputationImplementationGateValidationError):
        validate_transport_computation_implementation_gate(bad)


def test_validate_wrong_source_operator_hash_raises() -> None:
    gate = build_transport_computation_implementation_gate()
    bad = {**gate, "source_operator_decision_hash": "b" * 64}
    with pytest.raises(TransportComputationImplementationGateValidationError):
        validate_transport_computation_implementation_gate(bad)


def test_validate_false_transport_authorized_raises() -> None:
    gate = build_transport_computation_implementation_gate()
    bad_locks = {**gate["authority_locks"], "transport_computation_implementation_authorized": False}
    bad = {**gate, "authority_locks": bad_locks}
    with pytest.raises(TransportComputationImplementationGateValidationError):
        validate_transport_computation_implementation_gate(bad)


def test_validate_true_blocking_lock_raises() -> None:
    gate = build_transport_computation_implementation_gate()
    bad_locks = {**gate["authority_locks"], "emits_metric_values": True}
    bad = {**gate, "authority_locks": bad_locks}
    with pytest.raises(TransportComputationImplementationGateValidationError):
        validate_transport_computation_implementation_gate(bad)


def test_validate_constants_count_wrong_raises() -> None:
    gate = build_transport_computation_implementation_gate()
    bad_lc = {**gate["locked_constants_binding"], "constants_count": 5}
    bad_scope = {**gate["authorized_implementation_scope"], "locked_constants_binding": bad_lc}
    bad = {**gate, "authorized_implementation_scope": bad_scope,
           "locked_constants_binding": bad_lc}
    with pytest.raises(TransportComputationImplementationGateValidationError):
        validate_transport_computation_implementation_gate(bad)


# ── JSON schema ────────────────────────────────────────────────────────────────

def test_json_schema_validates_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/transport_computation_implementation_gate.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    gate = build_transport_computation_implementation_gate()
    jsonschema.validate(gate, schema)


# ── artifact file presence (post-runner) ──────────────────────────────────────

def test_gate_artifact_written() -> None:
    p = Path(
        "out/metric_operator/transport_computation_implementation_gate_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["gate_status"] == GATE_STATUS
    assert data["operator_id"] == OPERATOR_ID
    assert data["authority_locks"]["transport_computation_implementation_authorized"] is True
    assert data["authority_locks"]["lp_solver_invocation_authorized_for_test_vectors"] is True
    assert data["authority_locks"]["emits_metric_values"] is False
