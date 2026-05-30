from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ImplementationAuthorizationPrep.v1"
PREP_TYPE = "IMPLEMENTATION_AUTHORIZATION_PREP"
ALLOWED_READINESS_LEVEL = ("LOW", "MEDIUM", "HIGH", "NONE", "NOT_COMPUTABLE")
ALLOWED_IMPLEMENTATION_PATH = (
    "CPU_REFERENCE_CLOSED_FORM",
    "DEGENERATE_CASES_FIRST_THEN_LP",
    "NOT_COMPUTABLE_ONLY",
)
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
    "executable",
    "callable",
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class ImplementationAuthorizationPrepValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


READINESS_COMPARISON_KEYS = (
    "fixture_complexity",
    "numerical_risk",
    "deterministic_implementation_risk",
    "solver_dependency_risk",
    "expected_test_surface_size",
    "governance_risk",
    "fastest_safe_implementation_path",
)


def default_readiness_comparison() -> dict[str, Any]:
    return {
        "NORM_GEOMETRY": {
            "fixture_complexity": "MEDIUM",
            "numerical_risk": "MEDIUM",
            "deterministic_implementation_risk": "LOW",
            "solver_dependency_risk": "NONE",
            "expected_test_surface_size": "SMALL",
            "governance_risk": "LOW",
            "fastest_safe_implementation_path": "CPU_REFERENCE_CLOSED_FORM",
            "implementation_path_notes": (
                "Closed-form Lp norm: element-wise difference, absolute value, "
                "power, summation, root extraction. All float64 arithmetic. "
                "No external LP solver required. Degenerate paths: p=1 (no root), "
                "p=2 (standard square root), p=inf (max of absolute values). "
                "Fully deterministic without any external library or pivot-rule "
                "policy. Blocked scopes: lp_norm_computation, distance_emission."
            ),
        },
        "TRANSPORT": {
            "fixture_complexity": "MEDIUM",
            "numerical_risk": "MEDIUM",
            "deterministic_implementation_risk": "MEDIUM",
            "solver_dependency_risk": "HIGH",
            "expected_test_surface_size": "MEDIUM",
            "governance_risk": "LOW",
            "fastest_safe_implementation_path": "DEGENERATE_CASES_FIRST_THEN_LP",
            "implementation_path_notes": (
                "Discrete balanced optimal transport on a finite cost matrix. "
                "Degenerate cases (m=1, n=1, 1x1) are closed-form float64 "
                "weighted sums requiring no LP. General m*n case requires an "
                "LP solver; solver variant, pivot rule, and tie-breaking strategy "
                "are not yet locked. Balance tolerance (epsilon_rel) not yet "
                "locked. LP solver non-determinism risk for degenerate problems "
                "(multiple optimal transport plans) requires explicit tie-breaking "
                "policy before implementation can begin."
            ),
        },
    }


def default_required_operator_decision_fields() -> list[dict[str, Any]]:
    return [
        {
            "operator_id": "NORM_GEOMETRY",
            "required_decisions": [
                {
                    "decision_id": "ng-decision-001",
                    "field_name": "float64_precision_declaration",
                    "description": (
                        "Confirm that all element-wise differences, power operations, "
                        "summation accumulation, and root extraction must use float64. "
                        "Float32 excluded."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "ng-decision-002",
                    "field_name": "p_inf_sentinel_value_declaration",
                    "description": (
                        "Declare the exact sentinel value used to represent p=inf "
                        "in input data. Required before implementation to ensure "
                        "deterministic branch selection."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "ng-decision-003",
                    "field_name": "max_element_magnitude_declaration",
                    "description": (
                        "Declare the maximum allowed element magnitude in input "
                        "vectors. Required to bound power overflow risk."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "ng-decision-004",
                    "field_name": "max_p_value_declaration",
                    "description": (
                        "Declare the maximum allowed p value. Required to bound "
                        "power overflow risk for finite p."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "ng-decision-005",
                    "field_name": "not_computable_branch_enumeration_confirmation",
                    "description": (
                        "Confirm the complete enumeration of NOT_COMPUTABLE "
                        "conditions: empty vector, p < 1.0, mismatched lengths, "
                        "non-finite element, power overflow."
                    ),
                    "locked": False,
                },
            ],
        },
        {
            "operator_id": "TRANSPORT",
            "required_decisions": [
                {
                    "decision_id": "tr-decision-001",
                    "field_name": "lp_solver_variant_declaration",
                    "description": (
                        "Declare the exact LP solver variant to be used for "
                        "general m*n balanced transport problems. Must be a "
                        "deterministic solver with a fixed algorithm family."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "tr-decision-002",
                    "field_name": "pivot_rule_declaration",
                    "description": (
                        "Declare the exact pivot rule for the LP solver. "
                        "Stochastic or randomized pivot rules excluded."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "tr-decision-003",
                    "field_name": "tie_breaking_rule_declaration",
                    "description": (
                        "Declare the tie-breaking rule for degenerate transport "
                        "problems with multiple optimal transport plans. "
                        "Required for deterministic fixture matching."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "tr-decision-004",
                    "field_name": "balance_tolerance_declaration",
                    "description": (
                        "Declare the exact relative balance tolerance epsilon_rel. "
                        "Planned value: 1e-9 * max(sum(supply), sum(demand)). "
                        "Must be locked before implementation."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "tr-decision-005",
                    "field_name": "max_problem_size_declaration",
                    "description": (
                        "Declare the maximum allowed m*n problem size (number of "
                        "LP decision variables). Required to bound LP solve time "
                        "and memory usage."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "tr-decision-006",
                    "field_name": "cost_matrix_magnitude_bound_declaration",
                    "description": (
                        "Declare the maximum allowed cost matrix entry value. "
                        "Required to bound float64 overflow risk in the "
                        "LP objective accumulation."
                    ),
                    "locked": False,
                },
                {
                    "decision_id": "tr-decision-007",
                    "field_name": "not_computable_branch_enumeration_confirmation",
                    "description": (
                        "Confirm the complete enumeration of NOT_COMPUTABLE "
                        "conditions: empty supply/demand, unbalanced, negative "
                        "element, non-finite value, cost_matrix shape mismatch."
                    ),
                    "locked": False,
                },
            ],
        },
    ]


def default_locked_constants_required() -> dict[str, list[str]]:
    return {
        "NORM_GEOMETRY": [
            "float64_precision_declaration",
            "p_inf_sentinel_value_declaration",
            "max_element_magnitude_declaration",
            "max_p_value_declaration",
            "not_computable_branch_enumeration_confirmation",
        ],
        "TRANSPORT": [
            "lp_solver_variant_declaration",
            "pivot_rule_declaration",
            "tie_breaking_rule_declaration",
            "balance_tolerance_declaration",
            "max_problem_size_declaration",
            "cost_matrix_magnitude_bound_declaration",
            "not_computable_branch_enumeration_confirmation",
        ],
    }


def default_recommendation_rationale() -> dict[str, str]:
    return {
        "primary_reason": (
            "NORM_GEOMETRY is recommended as the first implementation path "
            "because it is closed-form and has no LP solver dependency. "
            "All Lp norm computation paths are deterministic float64 arithmetic "
            "with no external library or pivot-rule policy decisions required. "
            "Five locked constants are needed before NORM_GEOMETRY implementation "
            "can begin; all are well-defined and operator-decidable without "
            "external policy discovery."
        ),
        "secondary_reason": (
            "TRANSPORT implementation requires seven locked constants, five of "
            "which depend on LP solver policy decisions (solver variant, pivot "
            "rule, tie-breaking rule, balance tolerance, max problem size). "
            "These cannot be resolved without explicit operator policy choices "
            "that are independent of NORM_GEOMETRY implementation."
        ),
        "blocking_factors_for_transport": (
            "LP solver variant not declared; pivot rule not declared; "
            "tie-breaking strategy not declared; balance tolerance epsilon_rel "
            "not locked; cost matrix magnitude bound not locked. "
            "All five must be resolved before TRANSPORT implementation begins."
        ),
        "norm_geometry_relative_advantage": (
            "No solver dependency risk (NONE vs HIGH for TRANSPORT). "
            "Lower deterministic implementation risk (LOW vs MEDIUM). "
            "Smaller expected test surface (SMALL vs MEDIUM). "
            "Fixture uniqueness guaranteed for all valid test cases."
        ),
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_prep_artifact": True,
        "authorization_granted": False,
    }


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise ImplementationAuthorizationPrepValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_implementation_authorization_prep(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "prep_id", "prep_type", "operators_compared",
        "readiness_comparison", "recommended_first_implementation_path",
        "recommendation_rationale", "required_operator_decision_fields",
        "locked_constants_required", "authorization_granted",
        "authorization_prep_complete", "output_contract",
        "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise ImplementationAuthorizationPrepValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ImplementationAuthorizationPrepValidationError("invalid_schema_version")
    if packet["prep_type"] != PREP_TYPE:
        raise ImplementationAuthorizationPrepValidationError("invalid_prep_type")
    if packet["authorization_granted"] is not False:
        raise ImplementationAuthorizationPrepValidationError(
            "authorization_granted_must_be_false"
        )
    if packet["authorization_prep_complete"] is not True:
        raise ImplementationAuthorizationPrepValidationError(
            "authorization_prep_complete_must_be_true"
        )

    ops = packet["operators_compared"]
    if not ops:
        raise ImplementationAuthorizationPrepValidationError(
            "operators_compared_must_be_non_empty"
        )
    rc = packet["readiness_comparison"]
    for op in ops:
        if op not in rc:
            raise ImplementationAuthorizationPrepValidationError(
                f"readiness_comparison_missing_operator:{op}"
            )
        op_rc = rc[op]
        for key in READINESS_COMPARISON_KEYS:
            if key not in op_rc:
                raise ImplementationAuthorizationPrepValidationError(
                    f"readiness_comparison_missing_key:{op}:{key}"
                )
        if op_rc.get("solver_dependency_risk") not in ALLOWED_READINESS_LEVEL:
            raise ImplementationAuthorizationPrepValidationError(
                f"unknown_solver_dependency_risk:{op}"
            )
        if op_rc.get("fastest_safe_implementation_path") not in ALLOWED_IMPLEMENTATION_PATH:
            raise ImplementationAuthorizationPrepValidationError(
                f"unknown_fastest_safe_implementation_path:{op}"
            )

    rec_first = packet["recommended_first_implementation_path"]
    if rec_first not in ops:
        raise ImplementationAuthorizationPrepValidationError(
            "recommended_first_not_in_operators_compared"
        )

    rodfs = packet["required_operator_decision_fields"]
    if not rodfs:
        raise ImplementationAuthorizationPrepValidationError(
            "required_operator_decision_fields_must_be_non_empty"
        )
    for entry in rodfs:
        if not entry.get("required_decisions"):
            raise ImplementationAuthorizationPrepValidationError(
                f"required_decisions_must_be_non_empty:{entry.get('operator_id')}"
            )

    lcr = packet["locked_constants_required"]
    if not lcr:
        raise ImplementationAuthorizationPrepValidationError(
            "locked_constants_required_must_be_non_empty"
        )

    if packet["output_contract"] != default_output_contract():
        raise ImplementationAuthorizationPrepValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ImplementationAuthorizationPrepValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_implementation_authorization_prep_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_implementation_authorization_prep(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_implementation_authorization_prep(payload: dict[str, Any]) -> dict[str, Any]:
    ops = sorted(payload.get("operators_compared", []))
    rodfs = sorted(
        payload.get(
            "required_operator_decision_fields",
            default_required_operator_decision_fields(),
        ),
        key=lambda x: x["operator_id"],
    )
    for entry in rodfs:
        entry["required_decisions"] = sorted(
            entry.get("required_decisions", []),
            key=lambda d: d["decision_id"],
        )
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "prep_type": PREP_TYPE,
        "operators_compared": ops,
        "readiness_comparison": payload.get(
            "readiness_comparison", default_readiness_comparison()
        ),
        "recommended_first_implementation_path": payload.get(
            "recommended_first_implementation_path", "NORM_GEOMETRY"
        ),
        "recommendation_rationale": payload.get(
            "recommendation_rationale", default_recommendation_rationale()
        ),
        "required_operator_decision_fields": rodfs,
        "locked_constants_required": payload.get(
            "locked_constants_required", default_locked_constants_required()
        ),
        "authorization_granted": False,
        "authorization_prep_complete": True,
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_implementation_authorization_prep_hash(base)
    validate_implementation_authorization_prep(base)
    return _finalize(base)
