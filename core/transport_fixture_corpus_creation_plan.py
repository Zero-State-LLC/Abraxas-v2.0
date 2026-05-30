from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportFixtureCorpusCreationPlan.v1"
PLAN_STATUS = "TRANSPORT_FIXTURE_CORPUS_CREATION_PLAN_DEFINED"
PLAN_STAGE = "FIXTURE_CORPUS_CREATION_PLAN_ONLY"
OPERATOR_ID = "TRANSPORT"

SOURCE_IMPLEMENTATION_GATE_HASH = (
    "a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0"
)
SOURCE_DECISION_RECORD_HASH = (
    "2cd378187842043c93d4a66ed6e0f6a83b59cc1a3a8415c259abd70e5e1cb935"
)

IMPLEMENTATION_GATE_PATH = pathlib.Path(
    "out/metric_operator/"
    "transport_computation_implementation_gate_001.latest.json"
)

VALID_FIXTURE_IDS = (
    "tv-valid-001",
    "tv-valid-002",
    "tv-valid-003",
    "tv-valid-004",
    "tv-valid-005",
    "tv-valid-006",
)
INVALID_FIXTURE_IDS = (
    "tv-invalid-001",
    "tv-invalid-002",
    "tv-invalid-003",
    "tv-invalid-004",
)
NC_FIXTURE_IDS = (
    "tv-nc-001",
    "tv-nc-002",
    "tv-nc-003",
    "tv-nc-004",
    "tv-nc-005",
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_PLAN_STAGE = ("FIXTURE_CORPUS_CREATION_PLAN_ONLY",)
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY",)

FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-computation", "metric-value",
    "geodesic-distance", "numpy", "scipy", "gpu-kernel",
    "dijkstra-execution", "shortest-path-computation",
    "fixture-file", "manifest-file", "schema-file",
)


class TransportFixtureCorpusCreationPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportFixtureCorpusCreationPlanValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _verify_implementation_gate() -> dict[str, Any]:
    doc = json.loads(IMPLEMENTATION_GATE_PATH.read_text())
    h = doc.get("canonical_hash", "")
    if h != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"implementation_gate canonical_hash mismatch: stored={h!r}"
        )
    if doc.get("gate_status") != "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE_READY":
        raise TransportFixtureCorpusCreationPlanValidationError(
            "implementation_gate.gate_status mismatch"
        )
    if doc.get("source_decision_record_hash") != SOURCE_DECISION_RECORD_HASH:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "implementation_gate.source_decision_record_hash mismatch"
        )
    locks = doc.get("authority_locks", {})
    if locks.get("transport_computation_implementation_authorized") is not True:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "implementation_gate.transport_computation_implementation_authorized must be True"
        )
    return doc


def _build_locked_constants_binding(gate: dict[str, Any]) -> dict[str, Any]:
    lcb = gate.get("locked_constants_binding", {})
    return {
        "lp_solver_variant_declaration": lcb.get("lp_solver_variant_declaration"),
        "pivot_rule_declaration": lcb.get("pivot_rule_declaration"),
        "tie_breaking_rule_declaration": lcb.get("tie_breaking_rule_declaration"),
        "balance_tolerance_declaration": lcb.get("balance_tolerance_declaration"),
        "max_problem_size_declaration": lcb.get("max_problem_size_declaration"),
        "cost_matrix_magnitude_bound_declaration": lcb.get(
            "cost_matrix_magnitude_bound_declaration"
        ),
        "not_computable_branch_enumeration_confirmation": lcb.get(
            "not_computable_branch_enumeration_confirmation", []
        ),
        "all_constants_locked": True,
        "constants_count": 7,
    }


def build_valid_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "tv-valid-001",
            "fixture_name": "balanced_2x2_diagonal_cost_zero",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "problem_shape": "2x2",
            "expected_transport_distance": 0.0,
            "expected_value_derivation": "closed_form_trivial",
            "computation_not_required_for_expected_value": True,
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only fixture: 2x2 balanced transport problem with zero cost "
                "on the diagonal; optimal assignment sends all mass along the diagonal "
                "at zero cost. Expected transport distance 0.0 by inspection."
            ),
        },
        {
            "fixture_plan_id": "tv-valid-002",
            "fixture_name": "balanced_2x2_off_diagonal_cost_two",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "problem_shape": "2x2",
            "expected_transport_distance": 2.0,
            "expected_value_derivation": "closed_form_trivial",
            "computation_not_required_for_expected_value": True,
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only fixture: 2x2 balanced transport problem where diagonal "
                "costs are 2 and off-diagonal costs are 0; optimal assignment sends "
                "all mass off-diagonal at total cost 2.0."
            ),
        },
        {
            "fixture_plan_id": "tv-valid-003",
            "fixture_name": "single_source_1x4_closed_form",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "problem_shape": "1x4",
            "expected_transport_distance": 2.5,
            "expected_value_derivation": "closed_form_trivial",
            "computation_not_required_for_expected_value": True,
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only fixture: 1x4 single-source transport problem; one supply node "
                "distributes to four demand nodes with uniform supply 0.25 each; "
                "weighted cost sum yields expected transport distance 2.5."
            ),
        },
        {
            "fixture_plan_id": "tv-valid-004",
            "fixture_name": "single_target_4x1_closed_form",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "problem_shape": "4x1",
            "expected_transport_distance": 2.5,
            "expected_value_derivation": "closed_form_trivial",
            "computation_not_required_for_expected_value": True,
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only fixture: 4x1 single-target transport problem; four supply nodes "
                "each with mass 0.25 converge on one demand node; "
                "weighted cost sum yields expected transport distance 2.5."
            ),
        },
        {
            "fixture_plan_id": "tv-valid-005",
            "fixture_name": "degenerate_1x1_balanced",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "problem_shape": "1x1",
            "expected_transport_distance": 3.0,
            "expected_value_derivation": "closed_form_trivial",
            "computation_not_required_for_expected_value": True,
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only fixture: degenerate 1x1 transport problem; one supply node "
                "with mass 1.0 sends to one demand node with cost 3.0; "
                "expected transport distance 3.0 by direct calculation."
            ),
        },
        {
            "fixture_plan_id": "tv-valid-006",
            "fixture_name": "balanced_3x3_metric_cost_uniform",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "problem_shape": "3x3",
            "expected_transport_distance": 0.0,
            "expected_value_derivation": "closed_form_trivial",
            "computation_not_required_for_expected_value": True,
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only fixture: 3x3 balanced transport problem with zero cost on "
                "the diagonal and uniform supply and demand; optimal diagonal assignment "
                "achieves total cost 0.0."
            ),
        },
    ]


def build_invalid_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "tv-invalid-001",
            "fixture_name": "missing_supply_vector",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "supply",
            "expected_failure": "INVALID_INPUT",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only invalid fixture: supply vector field absent from input; "
                "schema contract violated at the required-field level."
            ),
        },
        {
            "fixture_plan_id": "tv-invalid-002",
            "fixture_name": "missing_demand_vector",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "demand",
            "expected_failure": "INVALID_INPUT",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only invalid fixture: demand vector field absent from input; "
                "schema contract violated at the required-field level."
            ),
        },
        {
            "fixture_plan_id": "tv-invalid-003",
            "fixture_name": "missing_cost_matrix",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "cost_matrix",
            "expected_failure": "INVALID_INPUT",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only invalid fixture: cost_matrix field absent from input; "
                "schema contract violated at the required-field level."
            ),
        },
        {
            "fixture_plan_id": "tv-invalid-004",
            "fixture_name": "cost_matrix_shape_mismatch",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "invalid_reason": "COST_MATRIX_SHAPE_MISMATCH",
            "target_field": "cost_matrix",
            "expected_failure": "INVALID_INPUT",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only invalid fixture: cost_matrix dimensions do not match "
                "len(supply) x len(demand); shape contract violated."
            ),
        },
    ]


def build_not_computable_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "tv-nc-001",
            "fixture_name": "unbalanced_supply_demand",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "UNBALANCED_SUPPLY_DEMAND",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: sum(supply) != sum(demand); "
                "transport problem is infeasible and must yield NOT_COMPUTABLE state."
            ),
        },
        {
            "fixture_plan_id": "tv-nc-002",
            "fixture_name": "negative_supply_value",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "NEGATIVE_SUPPLY_VALUE",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: one or more supply entries are "
                "negative; physically meaningless and must yield NOT_COMPUTABLE state."
            ),
        },
        {
            "fixture_plan_id": "tv-nc-003",
            "fixture_name": "negative_cost_value",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "NEGATIVE_COST_VALUE",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: one or more cost_matrix entries are "
                "negative; not permitted by the sealed cost matrix bound and must "
                "yield NOT_COMPUTABLE state."
            ),
        },
        {
            "fixture_plan_id": "tv-nc-004",
            "fixture_name": "empty_supply_vector",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "EMPTY_SUPPLY_VECTOR",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: supply vector has length zero; "
                "transport problem has no sources and must yield NOT_COMPUTABLE state."
            ),
        },
        {
            "fixture_plan_id": "tv-nc-005",
            "fixture_name": "non_finite_supply_value",
            "plan_stage": PLAN_STAGE,
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "NON_FINITE_SUPPLY_VALUE",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: one or more supply entries are "
                "non-finite (inf or NaN); must yield NOT_COMPUTABLE state."
            ),
        },
    ]


def build_fixture_path_plan() -> dict[str, Any]:
    return {
        "base_path": "input/fixtures/transport/",
        "fixture_count": 15,
        "valid_fixture_count": 6,
        "invalid_fixture_count": 4,
        "not_computable_fixture_count": 5,
        "naming_convention": "{fixture_plan_id}.json",
        "fixture_files_exist": False,
        "fixture_files_created": False,
        "creation_authorized_by": "TRANSPORT_FIXTURE_CORPUS_CREATION",
        "creation_requires_separate_step": True,
    }


def build_expected_value_policy() -> dict[str, Any]:
    return {
        "valid_fixture_policy": (
            "Expected transport distance declared inline for all 6 valid fixtures. "
            "Values are derivable from closed-form mathematical analysis of the "
            "problem structure without LP solver invocation. "
            "All six values verified by inspection prior to plan emission."
        ),
        "invalid_fixture_policy": (
            "No expected transport distance for invalid fixtures. "
            "Expected outcome is INVALID_INPUT. "
            "Validation must reject the input before any computation attempt."
        ),
        "not_computable_fixture_policy": (
            "No expected transport distance for NOT_COMPUTABLE fixtures. "
            "Expected outcome is NOT_COMPUTABLE. "
            "Guard branches must intercept input and return NOT_COMPUTABLE "
            "before any LP solver invocation."
        ),
        "metric_emission_blocked": True,
        "lp_solver_invocation_in_plan_phase": False,
    }


def build_deterministic_ordering_policy() -> dict[str, Any]:
    return {
        "sort_by_fixture_plan_id": True,
        "canonical_hash_required": True,
        "nondeterministic_ordering_allowed": False,
        "replay_stable": True,
        "stable_serialization_required": True,
        "fixture_id_ordering": "lexicographic_ascending",
        "valid_first_then_invalid_then_not_computable": True,
    }


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "fixture_corpus_creation_plan_only": True,
        "transport_computation_implementation_authorized": True,
        "lp_solver_invocation_authorized_for_test_vectors": True,
        "fixture_files_created": False,
        "computation_executed": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def build_blocked_scopes() -> dict[str, Any]:
    return {
        "fixture_files_created": False,
        "computation_executed": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def _validate_valid_plan(plan: list[dict[str, Any]]) -> None:
    ids = tuple(g["fixture_plan_id"] for g in plan)
    if ids != VALID_FIXTURE_IDS:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"valid fixture plan IDs must be {VALID_FIXTURE_IDS}, got {ids}"
        )
    for g in plan:
        if g.get("plan_stage") != PLAN_STAGE:
            raise TransportFixtureCorpusCreationPlanValidationError(
                f"invalid plan_stage in valid fixture {g['fixture_plan_id']}"
            )
        if g.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise TransportFixtureCorpusCreationPlanValidationError(
                f"invalid implementation_status in valid fixture {g['fixture_plan_id']}"
            )
        if not isinstance(g.get("expected_transport_distance"), (int, float)):
            raise TransportFixtureCorpusCreationPlanValidationError(
                f"expected_transport_distance missing or non-numeric in {g['fixture_plan_id']}"
            )


def _validate_invalid_plan(plan: list[dict[str, Any]]) -> None:
    ids = tuple(g["fixture_plan_id"] for g in plan)
    if ids != INVALID_FIXTURE_IDS:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"invalid fixture plan IDs must be {INVALID_FIXTURE_IDS}, got {ids}"
        )
    for g in plan:
        if g.get("expected_failure") != "INVALID_INPUT":
            raise TransportFixtureCorpusCreationPlanValidationError(
                f"expected_failure must be INVALID_INPUT in {g['fixture_plan_id']}"
            )


def _validate_nc_plan(plan: list[dict[str, Any]]) -> None:
    ids = tuple(g["fixture_plan_id"] for g in plan)
    if ids != NC_FIXTURE_IDS:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"NC fixture plan IDs must be {NC_FIXTURE_IDS}, got {ids}"
        )
    for g in plan:
        if g.get("expected_state") != "NOT_COMPUTABLE":
            raise TransportFixtureCorpusCreationPlanValidationError(
                f"expected_state must be NOT_COMPUTABLE in {g['fixture_plan_id']}"
            )


def validate_transport_fixture_corpus_creation_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if plan.get("plan_status") != PLAN_STATUS:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"plan_status must be {PLAN_STATUS!r}"
        )
    if plan.get("plan_stage") != PLAN_STAGE:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"plan_stage must be {PLAN_STAGE!r}"
        )
    if plan.get("operator_id") != OPERATOR_ID:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if plan.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "source_implementation_gate_hash mismatch"
        )
    if plan.get("source_decision_record_hash") != SOURCE_DECISION_RECORD_HASH:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "source_decision_record_hash mismatch"
        )
    locks = plan.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only", "fixture_corpus_creation_plan_only",
        "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
    ):
        if locks.get(flag) is not True:
            raise TransportFixtureCorpusCreationPlanValidationError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "fixture_files_created", "computation_executed", "emits_metric_values",
        "forecast_influence", "p43_surface_lanes_authorized", "production_activation",
        "canon_promotion", "runtime_mutation", "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise TransportFixtureCorpusCreationPlanValidationError(
                f"authority_locks.{flag} must be False"
            )
    if len(plan.get("valid_fixture_plan", [])) != 6:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "valid_fixture_plan must contain exactly 6 entries"
        )
    if len(plan.get("invalid_fixture_plan", [])) != 4:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "invalid_fixture_plan must contain exactly 4 entries"
        )
    if len(plan.get("not_computable_fixture_plan", [])) != 5:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "not_computable_fixture_plan must contain exactly 5 entries"
        )
    fpp = plan.get("fixture_path_plan", {})
    if fpp.get("fixture_count") != 15:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "fixture_path_plan.fixture_count must be 15"
        )
    if fpp.get("fixture_files_created") is not False:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "fixture_path_plan.fixture_files_created must be False"
        )
    lcb = plan.get("locked_constants_binding", {})
    if lcb.get("all_constants_locked") is not True:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "locked_constants_binding.all_constants_locked must be True"
        )
    if lcb.get("constants_count") != 7:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "locked_constants_binding.constants_count must be 7"
        )
    h = plan.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise TransportFixtureCorpusCreationPlanValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(plan))
    if recomputed != h:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )


def build_transport_fixture_corpus_creation_plan(
    plan_id: str = "transport_fixture_corpus_creation_plan_001",
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    if intended_lane not in ALLOWED_LANE:
        raise TransportFixtureCorpusCreationPlanValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    gate = _verify_implementation_gate()
    locked_constants = _build_locked_constants_binding(gate)

    valid_plan = build_valid_fixture_plan()
    invalid_plan = build_invalid_fixture_plan()
    nc_plan = build_not_computable_fixture_plan()

    _validate_valid_plan(valid_plan)
    _validate_invalid_plan(invalid_plan)
    _validate_nc_plan(nc_plan)

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": plan_id,
        "operator_id": OPERATOR_ID,
        "plan_status": PLAN_STATUS,
        "plan_stage": PLAN_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": intended_lane,
        "source_implementation_gate_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "source_decision_record_hash": SOURCE_DECISION_RECORD_HASH,
        "valid_fixture_plan": valid_plan,
        "invalid_fixture_plan": invalid_plan,
        "not_computable_fixture_plan": nc_plan,
        "fixture_path_plan": build_fixture_path_plan(),
        "expected_value_policy": build_expected_value_policy(),
        "deterministic_ordering_policy": build_deterministic_ordering_policy(),
        "locked_constants_binding": locked_constants,
        "blocked_scopes": build_blocked_scopes(),
        "authority_locks": build_authority_locks(),
        "recommended_next_step": "TRANSPORT_FIXTURE_CORPUS_CREATION",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)
