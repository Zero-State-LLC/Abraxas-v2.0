from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.transport_fixture_corpus_creation_plan import (
    INVALID_FIXTURE_IDS,
    NC_FIXTURE_IDS,
    OPERATOR_ID,
    PLAN_STAGE,
    PLAN_STATUS,
    SCHEMA_VERSION,
    SOURCE_DECISION_RECORD_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    VALID_FIXTURE_IDS,
    TransportFixtureCorpusCreationPlanValidationError,
    build_authority_locks,
    build_blocked_scopes,
    build_deterministic_ordering_policy,
    build_expected_value_policy,
    build_fixture_path_plan,
    build_invalid_fixture_plan,
    build_not_computable_fixture_plan,
    build_transport_fixture_corpus_creation_plan,
    build_valid_fixture_plan,
    validate_transport_fixture_corpus_creation_plan,
)
from core.canonical.json import canonical_hash

# ── constant invariants ────────────────────────────────────────────────────────

def test_schema_version() -> None:
    assert SCHEMA_VERSION == "TransportFixtureCorpusCreationPlan.v1"


def test_plan_status() -> None:
    assert PLAN_STATUS == "TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_DEFINED"


def test_plan_stage() -> None:
    assert PLAN_STAGE == "FIXTURE_CORPUS_CREATION_PLAN_ONLY"


def test_operator_id() -> None:
    assert OPERATOR_ID == "TRANSPORT"


def test_six_valid_fixture_ids() -> None:
    assert len(VALID_FIXTURE_IDS) == 6


def test_four_invalid_fixture_ids() -> None:
    assert len(INVALID_FIXTURE_IDS) == 4


def test_five_nc_fixture_ids() -> None:
    assert len(NC_FIXTURE_IDS) == 5


def test_source_gate_hash_64_chars() -> None:
    assert len(SOURCE_IMPLEMENTATION_GATE_HASH) == 64


def test_source_decision_record_hash_64_chars() -> None:
    assert len(SOURCE_DECISION_RECORD_HASH) == 64


def test_source_gate_hash_matches_artifact() -> None:
    p = Path(
        "out/metric_operator/transport_computation_implementation_gate_001.latest.json"
    )
    if not p.exists():
        pytest.skip("gate artifact not present")
    data = json.loads(p.read_text())
    assert data["canonical_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH


# ── build_valid_fixture_plan ───────────────────────────────────────────────────

def test_valid_plan_six_entries() -> None:
    assert len(build_valid_fixture_plan()) == 6


def test_valid_plan_ids_match_constant() -> None:
    ids = tuple(g["fixture_plan_id"] for g in build_valid_fixture_plan())
    assert ids == VALID_FIXTURE_IDS


def test_valid_plan_all_planned_only() -> None:
    for g in build_valid_fixture_plan():
        assert g["implementation_status"] == "PLANNED_ONLY"


def test_valid_plan_all_have_expected_distance() -> None:
    for g in build_valid_fixture_plan():
        d = g.get("expected_transport_distance")
        assert isinstance(d, (int, float)), f"{g['fixture_plan_id']} missing expected_transport_distance"


def test_valid_plan_tv001_distance_zero() -> None:
    g = next(g for g in build_valid_fixture_plan() if g["fixture_plan_id"] == "tv-valid-001")
    assert g["expected_transport_distance"] == 0.0


def test_valid_plan_tv002_distance_two() -> None:
    g = next(g for g in build_valid_fixture_plan() if g["fixture_plan_id"] == "tv-valid-002")
    assert g["expected_transport_distance"] == 2.0


def test_valid_plan_tv003_distance_two_point_five() -> None:
    g = next(g for g in build_valid_fixture_plan() if g["fixture_plan_id"] == "tv-valid-003")
    assert g["expected_transport_distance"] == 2.5


def test_valid_plan_tv004_distance_two_point_five() -> None:
    g = next(g for g in build_valid_fixture_plan() if g["fixture_plan_id"] == "tv-valid-004")
    assert g["expected_transport_distance"] == 2.5


def test_valid_plan_tv005_distance_three() -> None:
    g = next(g for g in build_valid_fixture_plan() if g["fixture_plan_id"] == "tv-valid-005")
    assert g["expected_transport_distance"] == 3.0


def test_valid_plan_tv006_distance_zero() -> None:
    g = next(g for g in build_valid_fixture_plan() if g["fixture_plan_id"] == "tv-valid-006")
    assert g["expected_transport_distance"] == 0.0


def test_valid_plan_no_lp_solver_invocation() -> None:
    for g in build_valid_fixture_plan():
        assert g["computation_not_required_for_expected_value"] is True


def test_valid_plan_metric_values_blocked() -> None:
    for g in build_valid_fixture_plan():
        assert "metric_values" in g["blocked_outputs"]


# ── build_invalid_fixture_plan ─────────────────────────────────────────────────

def test_invalid_plan_four_entries() -> None:
    assert len(build_invalid_fixture_plan()) == 4


def test_invalid_plan_ids_match_constant() -> None:
    ids = tuple(g["fixture_plan_id"] for g in build_invalid_fixture_plan())
    assert ids == INVALID_FIXTURE_IDS


def test_invalid_plan_all_invalid_input() -> None:
    for g in build_invalid_fixture_plan():
        assert g["expected_failure"] == "INVALID_INPUT"


def test_invalid_plan_missing_supply() -> None:
    g = next(g for g in build_invalid_fixture_plan() if g["fixture_plan_id"] == "tv-invalid-001")
    assert g["target_field"] == "supply"


def test_invalid_plan_missing_demand() -> None:
    g = next(g for g in build_invalid_fixture_plan() if g["fixture_plan_id"] == "tv-invalid-002")
    assert g["target_field"] == "demand"


def test_invalid_plan_missing_cost_matrix() -> None:
    g = next(g for g in build_invalid_fixture_plan() if g["fixture_plan_id"] == "tv-invalid-003")
    assert g["target_field"] == "cost_matrix"


def test_invalid_plan_shape_mismatch() -> None:
    g = next(g for g in build_invalid_fixture_plan() if g["fixture_plan_id"] == "tv-invalid-004")
    assert g["invalid_reason"] == "COST_MATRIX_SHAPE_MISMATCH"


# ── build_not_computable_fixture_plan ─────────────────────────────────────────

def test_nc_plan_five_entries() -> None:
    assert len(build_not_computable_fixture_plan()) == 5


def test_nc_plan_ids_match_constant() -> None:
    ids = tuple(g["fixture_plan_id"] for g in build_not_computable_fixture_plan())
    assert ids == NC_FIXTURE_IDS


def test_nc_plan_all_not_computable() -> None:
    for g in build_not_computable_fixture_plan():
        assert g["expected_state"] == "NOT_COMPUTABLE"


def test_nc_plan_nc001_unbalanced() -> None:
    g = next(g for g in build_not_computable_fixture_plan() if g["fixture_plan_id"] == "tv-nc-001")
    assert g["not_computable_reason"] == "UNBALANCED_SUPPLY_DEMAND"


def test_nc_plan_nc002_negative_supply() -> None:
    g = next(g for g in build_not_computable_fixture_plan() if g["fixture_plan_id"] == "tv-nc-002")
    assert g["not_computable_reason"] == "NEGATIVE_SUPPLY_VALUE"


def test_nc_plan_nc003_negative_cost() -> None:
    g = next(g for g in build_not_computable_fixture_plan() if g["fixture_plan_id"] == "tv-nc-003")
    assert g["not_computable_reason"] == "NEGATIVE_COST_VALUE"


def test_nc_plan_nc004_empty_supply() -> None:
    g = next(g for g in build_not_computable_fixture_plan() if g["fixture_plan_id"] == "tv-nc-004")
    assert g["not_computable_reason"] == "EMPTY_SUPPLY_VECTOR"


def test_nc_plan_nc005_non_finite_supply() -> None:
    g = next(g for g in build_not_computable_fixture_plan() if g["fixture_plan_id"] == "tv-nc-005")
    assert g["not_computable_reason"] == "NON_FINITE_SUPPLY_VALUE"


# ── build_fixture_path_plan ────────────────────────────────────────────────────

def test_fixture_path_plan_count_15() -> None:
    fpp = build_fixture_path_plan()
    assert fpp["fixture_count"] == 15


def test_fixture_path_plan_base_path() -> None:
    fpp = build_fixture_path_plan()
    assert fpp["base_path"] == "input/fixtures/transport/"


def test_fixture_path_plan_files_not_created() -> None:
    fpp = build_fixture_path_plan()
    assert fpp["fixture_files_created"] is False
    assert fpp["fixture_files_exist"] is False


def test_fixture_path_plan_counts_add_up() -> None:
    fpp = build_fixture_path_plan()
    assert (
        fpp["valid_fixture_count"] + fpp["invalid_fixture_count"]
        + fpp["not_computable_fixture_count"]
    ) == fpp["fixture_count"]


# ── build_authority_locks ──────────────────────────────────────────────────────

def test_authority_locks_advisory_true() -> None:
    locks = build_authority_locks()
    assert locks["advisory_only"] is True


def test_authority_locks_shadow_lane_only_true() -> None:
    locks = build_authority_locks()
    assert locks["shadow_lane_only"] is True


def test_authority_locks_plan_only_true() -> None:
    locks = build_authority_locks()
    assert locks["fixture_corpus_creation_plan_only"] is True


def test_authority_locks_transport_authorized_true() -> None:
    locks = build_authority_locks()
    assert locks["transport_computation_implementation_authorized"] is True


def test_authority_locks_lp_solver_authorized_true() -> None:
    locks = build_authority_locks()
    assert locks["lp_solver_invocation_authorized_for_test_vectors"] is True


def test_authority_locks_all_blocking_false() -> None:
    locks = build_authority_locks()
    for key in (
        "fixture_files_created", "computation_executed", "emits_metric_values",
        "forecast_influence", "p43_surface_lanes_authorized", "production_activation",
        "canon_promotion", "runtime_mutation", "execution_authority", "inference_authority",
    ):
        assert locks[key] is False, f"authority_locks.{key} must be False"


# ── build_blocked_scopes ───────────────────────────────────────────────────────

def test_blocked_scopes_all_false() -> None:
    bs = build_blocked_scopes()
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


def test_blocked_scopes_ten_keys() -> None:
    assert len(build_blocked_scopes()) == 10


# ── policies ──────────────────────────────────────────────────────────────────

def test_expected_value_policy_lp_solver_not_invoked() -> None:
    policy = build_expected_value_policy()
    assert policy["lp_solver_invocation_in_plan_phase"] is False


def test_expected_value_policy_metric_emission_blocked() -> None:
    policy = build_expected_value_policy()
    assert policy["metric_emission_blocked"] is True


def test_deterministic_ordering_policy_sort_by_id() -> None:
    policy = build_deterministic_ordering_policy()
    assert policy["sort_by_fixture_plan_id"] is True


def test_deterministic_ordering_policy_no_nondeterminism() -> None:
    policy = build_deterministic_ordering_policy()
    assert policy["nondeterministic_ordering_allowed"] is False


# ── full build (reads disk) ────────────────────────────────────────────────────

def test_plan_builds_successfully() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["plan_status"] == PLAN_STATUS


def test_plan_schema_version() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["schema_version"] == SCHEMA_VERSION


def test_plan_operator_id() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["operator_id"] == "TRANSPORT"


def test_plan_plan_stage_value() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["plan_stage"] == PLAN_STAGE


def test_plan_source_gate_hash() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["source_implementation_gate_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH


def test_plan_source_decision_record_hash() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["source_decision_record_hash"] == SOURCE_DECISION_RECORD_HASH


def test_plan_valid_fixture_count_six() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert len(plan["valid_fixture_plan"]) == 6


def test_plan_invalid_fixture_count_four() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert len(plan["invalid_fixture_plan"]) == 4


def test_plan_nc_fixture_count_five() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert len(plan["not_computable_fixture_plan"]) == 5


def test_plan_fixture_path_plan_count() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["fixture_path_plan"]["fixture_count"] == 15


def test_plan_locked_constants_count_seven() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["locked_constants_binding"]["constants_count"] == 7


def test_plan_authority_locks_transport_true() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    locks = plan["authority_locks"]
    assert locks["transport_computation_implementation_authorized"] is True
    assert locks["lp_solver_invocation_authorized_for_test_vectors"] is True


def test_plan_authority_locks_all_blocking_false() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    locks = plan["authority_locks"]
    for key in (
        "fixture_files_created", "computation_executed", "emits_metric_values",
        "forecast_influence", "p43_surface_lanes_authorized", "production_activation",
        "canon_promotion", "runtime_mutation", "execution_authority", "inference_authority",
    ):
        assert locks[key] is False, f"authority_locks.{key} must be False"


def test_plan_recommended_next_step() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    assert plan["recommended_next_step"] == "TRANSPORT_FIXTURE_CORPUS_CREATION"


def test_plan_canonical_hash_64_chars() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_plan_canonical_hash_recomputable() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == plan["canonical_hash"]


def test_plan_deterministic() -> None:
    a = build_transport_fixture_corpus_creation_plan()
    b = build_transport_fixture_corpus_creation_plan()
    assert a["canonical_hash"] == b["canonical_hash"]


# ── validate round-trip ────────────────────────────────────────────────────────

def test_validate_passes_on_valid_plan() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    validate_transport_fixture_corpus_creation_plan(plan)


def test_validate_wrong_schema_version_raises() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    bad = {**plan, "schema_version": "Wrong.v1"}
    with pytest.raises(TransportFixtureCorpusCreationPlanValidationError):
        validate_transport_fixture_corpus_creation_plan(bad)


def test_validate_wrong_gate_hash_raises() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    bad = {**plan, "source_implementation_gate_hash": "a" * 64}
    with pytest.raises(TransportFixtureCorpusCreationPlanValidationError):
        validate_transport_fixture_corpus_creation_plan(bad)


def test_validate_wrong_decision_hash_raises() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    bad = {**plan, "source_decision_record_hash": "b" * 64}
    with pytest.raises(TransportFixtureCorpusCreationPlanValidationError):
        validate_transport_fixture_corpus_creation_plan(bad)


def test_validate_false_transport_authorized_raises() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    bad_locks = {**plan["authority_locks"],
                 "transport_computation_implementation_authorized": False}
    bad = {**plan, "authority_locks": bad_locks}
    with pytest.raises(TransportFixtureCorpusCreationPlanValidationError):
        validate_transport_fixture_corpus_creation_plan(bad)


def test_validate_true_fixture_files_created_raises() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    bad_locks = {**plan["authority_locks"], "fixture_files_created": True}
    bad = {**plan, "authority_locks": bad_locks}
    with pytest.raises(TransportFixtureCorpusCreationPlanValidationError):
        validate_transport_fixture_corpus_creation_plan(bad)


def test_validate_wrong_fixture_count_raises() -> None:
    plan = build_transport_fixture_corpus_creation_plan()
    bad_fpp = {**plan["fixture_path_plan"], "fixture_count": 10}
    bad = {**plan, "fixture_path_plan": bad_fpp}
    with pytest.raises(TransportFixtureCorpusCreationPlanValidationError):
        validate_transport_fixture_corpus_creation_plan(bad)


# ── JSON schema ────────────────────────────────────────────────────────────────

def test_json_schema_validates_output() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/transport_fixture_corpus_creation_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    plan = build_transport_fixture_corpus_creation_plan()
    jsonschema.validate(plan, schema)


# ── artifact file presence (post-runner) ──────────────────────────────────────

def test_artifact_written() -> None:
    p = Path(
        "out/metric_operator/transport_fixture_corpus_creation_plan_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["plan_status"] == PLAN_STATUS
    assert data["operator_id"] == "TRANSPORT"
    assert len(data["valid_fixture_plan"]) == 6
    assert len(data["invalid_fixture_plan"]) == 4
    assert len(data["not_computable_fixture_plan"]) == 5
