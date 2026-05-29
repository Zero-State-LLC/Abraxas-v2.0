from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinValidFixtureImplementationPlan.v1"
PLAN_TYPE = "WASSERSTEIN_VALID_FIXTURE_IMPLEMENTATION_PLAN"
OPERATOR_ID = "WASSERSTEIN"

ALLOWED_FIXTURE_FAMILY = (
    "DISTRIBUTION_PAIR_FIXTURES",
    "REFERENCE_VECTOR_FIXTURES",
    "WEIGHTED_HISTOGRAM_FIXTURES",
    "DEGENERATE_DISTRIBUTION_FIXTURES",
    "MIXED_VALID_FIXTURE_PLAN",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "IMPLEMENTATION_PLAN_ONLY",
    "FIXTURE_LAYOUT_ONLY",
    "MANIFEST_PLAN_ONLY",
    "BLOCKED_PENDING_OPERATOR_REVIEW",
)
ALLOWED_CASE_TYPE = (
    "DISTRIBUTION_PAIR_CASE",
    "REFERENCE_VECTOR_CASE",
    "WEIGHTED_HISTOGRAM_CASE",
    "DEGENERATE_DISTRIBUTION_CASE",
    "EQUAL_DISTRIBUTION_CASE",
    "ONE_DIMENSIONAL_CASE",
)
ALLOWED_GROUND_METRIC = (
    "EUCLIDEAN_DECLARED",
    "UNIT_SIMPLEX_SPACE",
    "ABSTRACT_METRIC_SPACE",
    "NOT_COMPUTABLE_SPACE",
)
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
LOCKED_FALSE_FLAGS = (
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "runtime_mutation",
    "forecast_influence",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
)
FORBIDDEN = (
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-value",
    "wasserstein-distance",
    "expected-wasserstein",
    "earth-mover",
    "ot-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "sinkhorn-kernel",
)


class WassersteinValidFixtureImplementationPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_valid_fixture_cases() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "case-001",
            "case_type": "REFERENCE_VECTOR_CASE",
            "description": (
                "Plan-only 1D reference vector fixture: two distributions on R with "
                "known analytic Wasserstein-1 result declared without computed values."
            ),
            "planned_distribution_a_shape": "N weights + N support points",
            "planned_distribution_b_shape": "N weights + N support points",
            "ground_metric": "EUCLIDEAN_DECLARED",
            "dimensionality": 1,
            "expected_semantics": "reference_case_declared_without_wasserstein_values",
            "blocked_outputs": ["expected_wasserstein_distances"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "case_id": "case-002",
            "case_type": "DISTRIBUTION_PAIR_CASE",
            "description": (
                "Plan-only standard distribution pair: two normalized discrete distributions "
                "with non-overlapping support."
            ),
            "planned_distribution_a_shape": "N weights + N support points",
            "planned_distribution_b_shape": "M weights + M support points",
            "ground_metric": "EUCLIDEAN_DECLARED",
            "dimensionality": 1,
            "expected_semantics": "distribution_pair_declared_without_wasserstein_values",
            "blocked_outputs": ["expected_wasserstein_distances"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "case_id": "case-003",
            "case_type": "EQUAL_DISTRIBUTION_CASE",
            "description": (
                "Plan-only equal-distribution fixture: identical distributions "
                "where Wasserstein distance is analytically zero."
            ),
            "planned_distribution_a_shape": "N weights + N support points",
            "planned_distribution_b_shape": "N weights + N support points",
            "ground_metric": "EUCLIDEAN_DECLARED",
            "dimensionality": 1,
            "expected_semantics": "equal_case_declared_without_wasserstein_values",
            "blocked_outputs": ["expected_wasserstein_distances"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "case_id": "case-004",
            "case_type": "WEIGHTED_HISTOGRAM_CASE",
            "description": (
                "Plan-only weighted histogram fixture: distributions expressed as "
                "parallel weight and support arrays, pre-normalised."
            ),
            "planned_distribution_a_shape": "N weights + N support points",
            "planned_distribution_b_shape": "N weights + N support points",
            "ground_metric": "UNIT_SIMPLEX_SPACE",
            "dimensionality": 1,
            "expected_semantics": "weighted_histogram_declared_without_wasserstein_values",
            "blocked_outputs": ["expected_wasserstein_distances"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "case_id": "case-005",
            "case_type": "DEGENERATE_DISTRIBUTION_CASE",
            "description": (
                "Plan-only degenerate distribution fixture: single non-zero weight entry; "
                "all mass at one support point."
            ),
            "planned_distribution_a_shape": "1 weight + 1 support point",
            "planned_distribution_b_shape": "1 weight + 1 support point",
            "ground_metric": "EUCLIDEAN_DECLARED",
            "dimensionality": 1,
            "expected_semantics": "degenerate_case_declared_without_wasserstein_values",
            "blocked_outputs": ["expected_wasserstein_distances"],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_fixture_manifest_plan() -> dict[str, bool]:
    return {
        "manifest_declared": True,
        "manifest_file_added": False,
        "fixture_files_added": False,
        "fixture_ids_declared": True,
        "deterministic_sorting_declared": True,
        "expected_metric_values_declared": False,
    }


def default_deterministic_ordering_plan() -> dict[str, bool]:
    return {
        "sort_by_case_id": True,
        "stable_serialization_required": True,
        "canonical_hash_required": True,
        "nondeterministic_ordering_allowed": False,
    }


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_case_shape_tests": True,
        "requires_manifest_shape_tests": True,
        "requires_schema_validation": True,
        "requires_no_fixture_file_scan": True,
        "requires_no_expected_wasserstein_distance_scan": True,
        "requires_no_metric_value_scan": True,
        "requires_no_authority_scan": True,
    }


def default_fixture_constraints() -> dict[str, bool]:
    return {
        "fixture_files_added": False,
        "manifest_file_added": False,
        "expected_wasserstein_distances_added": False,
        "metric_values_added": False,
        "wasserstein_math_added": False,
        "scoring_added": False,
        "runtime_binding_added": False,
        "forecast_influence_added": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_fixture_files": False,
        "emits_manifest_file": False,
        "emits_expected_wasserstein_distances": False,
        "emits_metric_values": False,
        "emits_wasserstein_outputs": False,
        "emits_scores": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_valid_fixture_plan": True,
        "emits_fixture_case_metadata": True,
    }


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise WassersteinValidFixtureImplementationPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_wasserstein_valid_fixture_implementation_plan(packet: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "plan_id",
        "plan_type",
        "operator_id",
        "source_schema_plan_refs",
        "source_dossier_refs",
        "valid_fixture_scope",
        "valid_fixture_cases",
        "fixture_manifest_plan",
        "deterministic_ordering_plan",
        "validation_plan",
        "fixture_constraints",
        "output_contract",
        "governance_flags",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinValidFixtureImplementationPlanValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinValidFixtureImplementationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise WassersteinValidFixtureImplementationPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinValidFixtureImplementationPlanValidationError("unknown_operator_id")

    scope = packet["valid_fixture_scope"]
    if scope.get("fixture_family") not in ALLOWED_FIXTURE_FAMILY:
        raise WassersteinValidFixtureImplementationPlanValidationError("unknown_fixture_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise WassersteinValidFixtureImplementationPlanValidationError("unknown_intended_lane")
    if scope.get("implementation_stage") not in ALLOWED_STAGE:
        raise WassersteinValidFixtureImplementationPlanValidationError(
            "unknown_implementation_stage"
        )

    cases = packet["valid_fixture_cases"]
    if not cases:
        raise WassersteinValidFixtureImplementationPlanValidationError(
            "valid_fixture_cases_must_be_non_empty"
        )
    seen: set[str] = set()
    for case in cases:
        cid = case.get("case_id")
        if cid in seen:
            raise WassersteinValidFixtureImplementationPlanValidationError("duplicate_case_id")
        seen.add(cid)
        if case.get("case_type") not in ALLOWED_CASE_TYPE:
            raise WassersteinValidFixtureImplementationPlanValidationError("unknown_case_type")
        if case.get("ground_metric") not in ALLOWED_GROUND_METRIC:
            raise WassersteinValidFixtureImplementationPlanValidationError(
                "unknown_ground_metric"
            )
        if case.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise WassersteinValidFixtureImplementationPlanValidationError(
                "unknown_implementation_status"
            )
        if not isinstance(case.get("dimensionality"), int) or case["dimensionality"] <= 0:
            raise WassersteinValidFixtureImplementationPlanValidationError(
                "invalid_dimensionality"
            )

    if packet["fixture_manifest_plan"] != default_fixture_manifest_plan():
        raise WassersteinValidFixtureImplementationPlanValidationError(
            "invalid_fixture_manifest_plan"
        )
    if packet["deterministic_ordering_plan"] != default_deterministic_ordering_plan():
        raise WassersteinValidFixtureImplementationPlanValidationError(
            "invalid_deterministic_ordering_plan"
        )
    if packet["validation_plan"] != default_validation_plan():
        raise WassersteinValidFixtureImplementationPlanValidationError("invalid_validation_plan")
    if packet["fixture_constraints"] != default_fixture_constraints():
        raise WassersteinValidFixtureImplementationPlanValidationError(
            "invalid_fixture_constraints"
        )
    if packet["output_contract"] != default_output_contract():
        raise WassersteinValidFixtureImplementationPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise WassersteinValidFixtureImplementationPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )

    _assert_safe(packet["provenance"])


def compute_wasserstein_valid_fixture_implementation_plan_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_valid_fixture_implementation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_valid_fixture_implementation_plan(
    payload: dict[str, Any],
) -> dict[str, Any]:
    cases = sorted(
        payload.get("valid_fixture_cases", default_valid_fixture_cases()),
        key=lambda x: x["case_id"],
    )
    for case in cases:
        case["blocked_outputs"] = sorted(case.get("blocked_outputs", []))

    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_schema_plan_refs": sorted(payload.get("source_schema_plan_refs", [])),
        "source_dossier_refs": sorted(payload.get("source_dossier_refs", [])),
        "valid_fixture_cases": cases,
        "fixture_manifest_plan": payload.get(
            "fixture_manifest_plan", default_fixture_manifest_plan()
        ),
        "deterministic_ordering_plan": payload.get(
            "deterministic_ordering_plan", default_deterministic_ordering_plan()
        ),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "fixture_constraints": payload.get(
            "fixture_constraints", default_fixture_constraints()
        ),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_wasserstein_valid_fixture_implementation_plan_hash(base)
    validate_wasserstein_valid_fixture_implementation_plan(base)
    return _finalize(base)
