from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.transport_implementation_authorization_decision_record import (
    build_transport_implementation_authorization_decision_record,
    default_authority_locks,
    default_blocked_scopes,
    default_output_contract,
    serialize_transport_implementation_authorization_decision_record,
    _build_blocked_scope_acknowledgement_review,
    _build_decision_validation_review,
    _build_implementation_gate_prerequisite_review,
    _build_locked_constants_record,
    REQUIRED_LOCKED_CONSTANT_KEYS,
    REQUIRED_ACKNOWLEDGEMENT_KEYS,
    SCHEMA_VERSION,
    RECORD_STATUS,
)
from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags as front_governance_flags,
    default_output_contract as front_output_contract,
    transport_implementation_gate_ranked_options,
)
from core.canonical.json import canonical_hash

PATCH_ID = "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORD_001"

_VALID_LOCKED_CONSTANTS = {
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
    "not_computable_branch_enumeration_confirmation": [
        "UNBALANCED_SUPPLY_DEMAND",
        "NEGATIVE_SUPPLY_VALUE",
        "NEGATIVE_COST_VALUE",
        "EMPTY_SUPPLY_VECTOR",
        "EMPTY_DEMAND_VECTOR",
        "NON_FINITE_SUPPLY_VALUE",
        "NON_FINITE_DEMAND_VALUE",
        "NON_FINITE_COST_VALUE",
        "COST_MATRIX_SHAPE_MISMATCH",
    ],
}

_VALID_DECISION_DATA = {
    "decision_id": "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_2026_05_29_001",
    "operator_id": "Daniel Meyer",
    "decision": "approve_transport_shadow_computation_implementation",
    "implementation_lane_authorized": "TEST_VECTOR_COMPUTATION_ONLY",
    "baseline_target": "SHADOW_STUB_ONLY",
    "locked_constants": _VALID_LOCKED_CONSTANTS,
    "shadow_lane_only_acknowledged": True,
    "test_vector_computation_only_acknowledged": True,
    "lp_solver_invocation_limited_to_test_vector_scope_acknowledged": True,
    "metric_values_emission_blocked_acknowledged": True,
    "forecast_influence_blocked_acknowledged": True,
    "p43_surface_lanes_blocked_acknowledged": True,
    "production_activation_blocked_acknowledged": True,
    "canon_promotion_blocked_acknowledged": True,
    "runtime_mutation_blocked_acknowledged": True,
    "execution_authority_blocked_acknowledged": True,
    "valid_for_execution": False,
    "authorization_granted": False,
    "emits_metric_values": False,
    "forecast_authority": False,
    "inference_authority": False,
    "production_activation": False,
    "canon_promotion": False,
    "runtime_mutation": False,
    "execution_authority": False,
}


def _make_payload(decision_data: dict | None = None) -> dict:
    dd = decision_data if decision_data is not None else _VALID_DECISION_DATA
    from core.canonical.json import canonical_hash as ch
    return {
        "record_id": "transport_implementation_authorization_decision_record_001",
        "source_operator_decision_hash": ch(dd),
        "decision_id": dd.get("decision_id", ""),
        "locked_constants_record": _build_locked_constants_record(
            dd.get("locked_constants", {})
        ),
        "decision_validation_review": _build_decision_validation_review(dd),
        "blocked_scope_acknowledgement_review": _build_blocked_scope_acknowledgement_review(dd),
        "implementation_gate_prerequisite_review": _build_implementation_gate_prerequisite_review(),
        "authority_locks": default_authority_locks(),
        "blocked_scopes": default_blocked_scopes(),
        "recommended_next_step": "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE",
        "output_contract": default_output_contract(),
        "provenance": {
            "source": "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORD_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "TransportImplementationAuthorizationOperatorDecision.v1"
                ":transport_implementation_authorization_operator_decision",
            ],
            "upstream_schema_refs": [
                "contracts/canon/transport_implementation_authorization_decision_record.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _make_frontier_payload() -> dict:
    return {
        "recommendation_id": "metric_operator_frontier_recommendation_006",
        "recommendation_status": "ADVISORY_ONLY",
        "ranked_options": transport_implementation_gate_ranked_options(),
        "recommended_next_step": "G_SEALED_PAUSE",
        "required_operator_decision": True,
        "stop_boundary_reason": (
            "TRANSPORT implementation authorization decision recorded. "
            "No self-authorizing advancement exists."
        ),
        "output_contract": front_output_contract(),
        "governance_flags": front_governance_flags(),
        "provenance": {
            "source": "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORD_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "TransportImplementationAuthorizationDecisionRecord.v1"
                ":transport_implementation_authorization_decision_record_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── _build_locked_constants_record ─────────────────────────────────────────────

def test_locked_constants_record_all_present() -> None:
    lcr = _build_locked_constants_record(_VALID_LOCKED_CONSTANTS)
    assert lcr["all_locked_constants_present"] is True


def test_locked_constants_record_valid_for_scope() -> None:
    lcr = _build_locked_constants_record(_VALID_LOCKED_CONSTANTS)
    assert lcr["constants_valid_for_test_vector_scope"] is True


def test_locked_constants_record_all_keys_present() -> None:
    lcr = _build_locked_constants_record(_VALID_LOCKED_CONSTANTS)
    for key in REQUIRED_LOCKED_CONSTANT_KEYS:
        assert key in lcr, f"missing key: {key}"


def test_locked_constants_record_seven_constants() -> None:
    assert len(REQUIRED_LOCKED_CONSTANT_KEYS) == 7


def test_locked_constants_record_missing_key_sets_false() -> None:
    incomplete = {k: v for k, v in _VALID_LOCKED_CONSTANTS.items()
                  if k != "pivot_rule_declaration"}
    lcr = _build_locked_constants_record(incomplete)
    assert lcr["all_locked_constants_present"] is False
    assert lcr["constants_valid_for_test_vector_scope"] is False


def test_locked_constants_not_computable_branches_nine() -> None:
    branches = _VALID_LOCKED_CONSTANTS["not_computable_branch_enumeration_confirmation"]
    assert len(branches) == 9


# ── _build_decision_validation_review ─────────────────────────────────────────

def test_decision_validation_review_valid() -> None:
    dvr = _build_decision_validation_review(_VALID_DECISION_DATA)
    assert dvr["decision_valid"] is True
    assert dvr["decision_match"] is True
    assert dvr["implementation_lane_match"] is True
    assert dvr["baseline_target_match"] is True
    assert dvr["all_authority_flags_false"] is True


def test_decision_validation_review_wrong_decision_fails() -> None:
    bad = {**_VALID_DECISION_DATA, "decision": "wrong_value"}
    dvr = _build_decision_validation_review(bad)
    assert dvr["decision_match"] is False
    assert dvr["decision_valid"] is False


def test_decision_validation_review_wrong_lane_fails() -> None:
    bad = {**_VALID_DECISION_DATA, "implementation_lane_authorized": "PRODUCTION"}
    dvr = _build_decision_validation_review(bad)
    assert dvr["implementation_lane_match"] is False
    assert dvr["decision_valid"] is False


def test_decision_validation_review_authority_flag_true_fails() -> None:
    bad = {**_VALID_DECISION_DATA, "valid_for_execution": True}
    dvr = _build_decision_validation_review(bad)
    assert dvr["all_authority_flags_false"] is False
    assert dvr["decision_valid"] is False


# ── _build_blocked_scope_acknowledgement_review ────────────────────────────────

def test_acknowledgement_review_all_confirmed() -> None:
    bsar = _build_blocked_scope_acknowledgement_review(_VALID_DECISION_DATA)
    assert bsar["all_acknowledgements_confirmed"] is True


def test_acknowledgement_review_ten_keys() -> None:
    assert len(REQUIRED_ACKNOWLEDGEMENT_KEYS) == 10


def test_acknowledgement_review_missing_ack_fails() -> None:
    bad = {**_VALID_DECISION_DATA}
    bad["shadow_lane_only_acknowledged"] = False
    bsar = _build_blocked_scope_acknowledgement_review(bad)
    assert bsar["shadow_lane_only_acknowledged"] is False
    assert bsar["all_acknowledgements_confirmed"] is False


# ── _build_implementation_gate_prerequisite_review ────────────────────────────

def test_prerequisites_met() -> None:
    prereqs = _build_implementation_gate_prerequisite_review()
    assert prereqs["prerequisites_met"] is True
    assert prereqs["seven_locked_constants_declared"] is True
    assert prereqs["four_operator_shadow_stub_parity_confirmed"] is True
    assert prereqs["transport_cpu_baseline_planning_complete"] is True


# ── default_authority_locks ────────────────────────────────────────────────────

def test_authority_locks_advisory_true() -> None:
    locks = default_authority_locks()
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["decision_record_only"] is True


def test_authority_locks_all_blocking_false() -> None:
    locks = default_authority_locks()
    for key in (
        "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert locks[key] is False, f"authority_locks.{key} must be False"


def test_authority_locks_lane_authorized() -> None:
    locks = default_authority_locks()
    assert locks["implementation_lane_authorized"] == "TEST_VECTOR_COMPUTATION_ONLY"


# ── default_blocked_scopes ─────────────────────────────────────────────────────

def test_blocked_scopes_eight_entries() -> None:
    scopes = default_blocked_scopes()
    assert len(scopes) == 8


def test_blocked_scopes_contains_lp_solver() -> None:
    scopes = default_blocked_scopes()
    assert "LP_SOLVER_INVOCATION_OUTSIDE_TEST_VECTOR_SCOPE" in scopes


def test_blocked_scopes_contains_metric_emission() -> None:
    scopes = default_blocked_scopes()
    assert "METRIC_EMISSION" in scopes


# ── build_transport_implementation_authorization_decision_record ───────────────

def test_record_builds_with_valid_payload() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    assert record["record_status"] == RECORD_STATUS
    assert record["schema_version"] == SCHEMA_VERSION


def test_record_operator_id_transport() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    assert record["operator_id"] == "TRANSPORT"


def test_record_implementation_lane_authorized() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    assert record["implementation_lane_authorized"] == "TEST_VECTOR_COMPUTATION_ONLY"


def test_record_baseline_target() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    assert record["baseline_target"] == "SHADOW_STUB_ONLY"


def test_record_recommended_next_step() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    assert record["recommended_next_step"] == "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE"


def test_record_deterministic() -> None:
    a = build_transport_implementation_authorization_decision_record(_make_payload())
    b = build_transport_implementation_authorization_decision_record(_make_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_record_hash_valid() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    h = record["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in record.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_record_authority_locks_all_false() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    locks = record["authority_locks"]
    for key in (
        "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        assert locks[key] is False, f"authority_locks.{key} must be False"


def test_record_output_contract_emits_decision_record() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    assert record["output_contract"]["emits_decision_record"] is True
    assert record["output_contract"]["emits_metric_values"] is False


def test_record_blocked_scopes_present() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    assert isinstance(record["blocked_scopes"], list)
    assert len(record["blocked_scopes"]) > 0


def test_record_source_decision_hash_64_chars() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    h = record["source_operator_decision_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_record_locked_constants_all_present() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    lcr = record["locked_constants_record"]
    assert lcr["all_locked_constants_present"] is True
    assert lcr["constants_valid_for_test_vector_scope"] is True


def test_record_prerequisites_met() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    prereqs = record["implementation_gate_prerequisite_review"]
    assert prereqs["prerequisites_met"] is True


def test_record_decision_validation_passed() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    dvr = record["decision_validation_review"]
    assert dvr["decision_valid"] is True


def test_record_acknowledgements_confirmed() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    bsar = record["blocked_scope_acknowledgement_review"]
    assert bsar["all_acknowledgements_confirmed"] is True


def test_serialize_ends_with_newline() -> None:
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    s = serialize_transport_implementation_authorization_decision_record(record)
    assert s.endswith("\n")


def test_schema_validates_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/"
            "transport_implementation_authorization_decision_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    record = build_transport_implementation_authorization_decision_record(_make_payload())
    jsonschema.validate(record, schema)


# ── transport_implementation_gate_ranked_options ───────────────────────────────

def test_transport_gate_ranked_options_count() -> None:
    opts = transport_implementation_gate_ranked_options()
    assert len(opts) == 6


def test_transport_gate_rank1_sealed_pause() -> None:
    opts = transport_implementation_gate_ranked_options()
    r1 = next(o for o in opts if o["rank"] == 1)
    assert r1["option_id"] == "G_SEALED_PAUSE"
    assert r1["authority_posture"] == "ADVISORY_ONLY"
    assert r1["requires_operator_instruction"] is False


def test_transport_gate_rank2_transport_gate() -> None:
    opts = transport_implementation_gate_ranked_options()
    r2 = next(o for o in opts if o["rank"] == 2)
    assert r2["option_id"] == "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE"
    assert r2["authority_posture"] == "ADVISORY_ONLY"
    assert r2["requires_operator_instruction"] is True


def test_transport_gate_rank3_rank6_selection() -> None:
    opts = transport_implementation_gate_ranked_options()
    r3 = next(o for o in opts if o["rank"] == 3)
    assert r3["option_id"] == "N_RANK6_OPERATOR_SELECTION"


def test_transport_gate_rank4_registry_hardening() -> None:
    opts = transport_implementation_gate_ranked_options()
    r4 = next(o for o in opts if o["rank"] == 4)
    assert r4["option_id"] == "M_REGISTRY_HARDENING"


def test_transport_gate_blocked_options() -> None:
    opts = transport_implementation_gate_ranked_options()
    blocked = {o["option_id"] for o in opts if o["authority_posture"] == "BLOCKED"}
    assert "C_METRIC_EMISSION_AUTHORIZATION_REVIEW" in blocked
    assert "E_P43_SURFACE_LANE_READINESS" in blocked


def test_transport_gate_unique_ranks() -> None:
    opts = transport_implementation_gate_ranked_options()
    ranks = [o["rank"] for o in opts]
    assert len(ranks) == len(set(ranks))


# ── Frontier Recommendation 006 ───────────────────────────────────────────────

def test_frontier_006_builds() -> None:
    rec = build_metric_operator_frontier_recommendation(_make_frontier_payload())
    assert rec["recommendation_status"] == "ADVISORY_ONLY"
    assert rec["recommendation_id"] == "metric_operator_frontier_recommendation_006"
    assert rec["recommended_next_step"] == "G_SEALED_PAUSE"


def test_frontier_006_deterministic() -> None:
    a = build_metric_operator_frontier_recommendation(_make_frontier_payload())
    b = build_metric_operator_frontier_recommendation(_make_frontier_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_frontier_006_hash_valid() -> None:
    rec = build_metric_operator_frontier_recommendation(_make_frontier_payload())
    h = rec["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in rec.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_frontier_006_governance_all_false() -> None:
    rec = build_metric_operator_frontier_recommendation(_make_frontier_payload())
    for flag, val in rec["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_frontier_006_transport_gate_advisory() -> None:
    rec = build_metric_operator_frontier_recommendation(_make_frontier_payload())
    gate = next(
        o for o in rec["ranked_options"]
        if o["option_id"] == "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE"
    )
    assert gate["authority_posture"] == "ADVISORY_ONLY"


def test_frontier_006_metric_emission_blocked() -> None:
    rec = build_metric_operator_frontier_recommendation(_make_frontier_payload())
    emission = next(
        o for o in rec["ranked_options"]
        if o["option_id"] == "C_METRIC_EMISSION_AUTHORIZATION_REVIEW"
    )
    assert emission["authority_posture"] == "BLOCKED"


def test_frontier_006_p43_blocked() -> None:
    rec = build_metric_operator_frontier_recommendation(_make_frontier_payload())
    p43 = next(
        o for o in rec["ranked_options"]
        if o["option_id"] == "E_P43_SURFACE_LANE_READINESS"
    )
    assert p43["authority_posture"] == "BLOCKED"


# ── Artifact file presence (post-runner) ──────────────────────────────────────

def test_decision_record_001_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "transport_implementation_authorization_decision_record_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["record_status"] == RECORD_STATUS
    assert data["operator_id"] == "TRANSPORT"
    assert data["implementation_lane_authorized"] == "TEST_VECTOR_COMPUTATION_ONLY"


def test_frontier_006_file_written() -> None:
    p = Path("out/metric_operator/metric_operator_frontier_recommendation_006.latest.json")
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["recommendation_status"] == "ADVISORY_ONLY"
    assert data["recommended_next_step"] == "G_SEALED_PAUSE"
