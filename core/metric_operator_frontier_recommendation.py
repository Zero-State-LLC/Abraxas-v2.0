from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricOperatorFrontierRecommendation.v1"

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

ALLOWED_RECOMMENDATION_STATUS = ("ADVISORY_ONLY", "BLOCKED")
ALLOWED_AUTHORITY_POSTURE = ("ADVISORY_ONLY", "BLOCKED")

FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-value",
)


class MetricOperatorFrontierRecommendationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_recommendation": True,
    }


def default_governance_flags() -> dict[str, bool]:
    return {flag: False for flag in LOCKED_FALSE_FLAGS}


def three_operator_default_ranked_options() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "option_id": "G_SEALED_PAUSE",
            "option_name": "Sealed pause / no-op",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": False,
            "first_lawful_step": None,
        },
        {
            "rank": 2,
            "option_id": "B_FOURTH_OPERATOR_SELECTION",
            "option_name": "Fourth metric operator selection",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Operator designates rank-4 operator ID from remaining 9 NOT_IMPLEMENTED "
                "operators. Emit MetricOperatorImplementationSelectionPlanUpdate.v1 with "
                "THIRD_OPERATOR_SELECTION scope. Requires explicit operator designation."
            ),
        },
        {
            "rank": 3,
            "option_id": "D_CPU_REFERENCE_IMPLEMENTATION_PLANNING",
            "option_name": "CPU reference implementation planning",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Emit CPU baseline implementation plan for WASSERSTEIN, CHAMFER_DISTANCE, "
                "or GEODESIC. Shadow-only, advisory, no execution authority."
            ),
        },
        {
            "rank": 4,
            "option_id": "H_REGISTRY_HARDENING",
            "option_name": "Registry hardening",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Emit MetricOperatorRegistryStabilization.v2 structured artifact confirming "
                "WASSERSTEIN, CHAMFER_DISTANCE, and GEODESIC at SHADOW_STUB_ONLY parity "
                "and all remaining operators unchanged."
            ),
        },
        {
            "rank": 5,
            "option_id": "C_METRIC_EMISSION_AUTHORIZATION_REVIEW",
            "option_name": "Metric emission authorization review",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful without separate operator-authorized governance design. "
                "No CPU reference implementation exists. Premature without Option D first."
            ),
        },
        {
            "rank": 6,
            "option_id": "E_P43_SURFACE_LANE_READINESS",
            "option_name": "P43 surface lane readiness",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. Explicitly blocked by current operator instruction. "
                "Requires separate operator-authorized governance design."
            ),
        },
    ]


def default_ranked_options() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "option_id": "G_SEALED_PAUSE",
            "option_name": "Sealed pause / no-op",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": False,
            "first_lawful_step": None,
        },
        {
            "rank": 2,
            "option_id": "F_REGISTRY_STABILIZATION",
            "option_name": "Metric registry stabilization update",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Emit MetricOperatorRegistryStabilization.v1 structured artifact "
                "reflecting WASSERSTEIN and CHAMFER_DISTANCE as SHADOW_STUB_ONLY "
                "and all other operators as NOT_IMPLEMENTED."
            ),
        },
        {
            "rank": 3,
            "option_id": "A_CROSS_OPERATOR_PARITY_REVIEW",
            "option_name": "Cross-operator parity review",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Emit MetricOperatorCrossOperatorParityReceipt.v1 confirming "
                "WASSERSTEIN and CHAMFER_DISTANCE are at equivalent SHADOW_STUB_ONLY posture."
            ),
        },
        {
            "rank": 4,
            "option_id": "D_CPU_REFERENCE_IMPLEMENTATION_PLANNING",
            "option_name": "CPU reference implementation planning",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Emit WassersteinBaselineImplementationPlan.v1 (no equivalent exists "
                "for WASSERSTEIN; ChamferBaselineImplementationPlan.v1 already present). "
                "Shadow-only, advisory, no execution authority."
            ),
        },
        {
            "rank": 5,
            "option_id": "B_THIRD_OPERATOR_SELECTION",
            "option_name": "Third metric operator selection",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Operator designates rank-3 operator ID from remaining 10 NOT_IMPLEMENTED "
                "operators. Emit MetricOperatorImplementationSelectionPlanUpdate.v1 with "
                "SECOND_OPERATOR_SELECTION scope. Requires explicit operator designation."
            ),
        },
        {
            "rank": 6,
            "option_id": "C_METRIC_EMISSION_AUTHORIZATION_REVIEW",
            "option_name": "Metric emission authorization review",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful without separate operator-authorized governance design. "
                "No CPU reference implementation exists. Premature without Option D first."
            ),
        },
        {
            "rank": 7,
            "option_id": "E_P43_SURFACE_LANE_READINESS",
            "option_name": "P43 surface lane readiness",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. Explicitly blocked by current operator instruction. "
                "Requires separate operator-authorized governance design."
            ),
        },
    ]


def four_operator_planned_ranked_options() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "option_id": "G_SEALED_PAUSE",
            "option_name": "Sealed pause / no-op",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": False,
            "first_lawful_step": None,
        },
        {
            "rank": 2,
            "option_id": "I_RANK5_OPERATOR_SELECTION",
            "option_name": "Rank-5 metric operator selection",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Operator designates rank-5 operator ID from remaining 8 "
                "NOT_IMPLEMENTED operators. Emit MetricOperatorRank5CandidateAudit.v1 "
                "and MetricOperatorRank5SelectionPlan.v1. Requires explicit "
                "operator designation."
            ),
        },
        {
            "rank": 3,
            "option_id": "J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION",
            "option_name": "NORM_GEOMETRY implementation authorization",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. gate-cond-005 unmet in "
                "NormGeometryCpuBaselineActualPrGateReview.v1. Operator explicit "
                "authorization instruction required before any NORM_GEOMETRY "
                "implementation PR may be opened."
            ),
        },
        {
            "rank": 4,
            "option_id": "C_METRIC_EMISSION_AUTHORIZATION_REVIEW",
            "option_name": "Metric emission authorization review",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful without separate operator-authorized governance design. "
                "No CPU reference implementation exists for any operator. "
                "Premature without NORM_GEOMETRY implementation authorization first."
            ),
        },
        {
            "rank": 5,
            "option_id": "E_P43_SURFACE_LANE_READINESS",
            "option_name": "P43 surface lane readiness",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. Explicitly blocked by current operator instruction. "
                "Requires separate operator-authorized governance design."
            ),
        },
    ]


def five_operator_planned_ranked_options() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "option_id": "G_SEALED_PAUSE",
            "option_name": "Sealed pause / no-op",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": False,
            "first_lawful_step": None,
        },
        {
            "rank": 2,
            "option_id": "J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION",
            "option_name": "NORM_GEOMETRY implementation authorization",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. gate-cond-005 unmet in "
                "NormGeometryCpuBaselineActualPrGateReview.v1. Operator explicit "
                "authorization instruction required before any NORM_GEOMETRY "
                "implementation PR may be opened."
            ),
        },
        {
            "rank": 3,
            "option_id": "K_TRANSPORT_IMPLEMENTATION_AUTHORIZATION",
            "option_name": "TRANSPORT implementation authorization",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. No CPU reference implementation plan exists for "
                "TRANSPORT. LP solver policy and fixture schema plan must be "
                "finalized before any implementation PR may be opened. Operator "
                "explicit authorization instruction required."
            ),
        },
        {
            "rank": 4,
            "option_id": "C_METRIC_EMISSION_AUTHORIZATION_REVIEW",
            "option_name": "Metric emission authorization review",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful without separate operator-authorized governance design. "
                "No CPU reference implementation exists for any operator. "
                "Premature without at least one operator implementation authorization first."
            ),
        },
        {
            "rank": 5,
            "option_id": "E_P43_SURFACE_LANE_READINESS",
            "option_name": "P43 surface lane readiness",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. Explicitly blocked by current operator instruction. "
                "Requires separate operator-authorized governance design."
            ),
        },
    ]


def transport_implementation_gate_ranked_options() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "option_id": "G_SEALED_PAUSE",
            "option_name": "Sealed pause / no-op",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": False,
            "first_lawful_step": None,
        },
        {
            "rank": 2,
            "option_id": "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE",
            "option_name": "TRANSPORT computation implementation gate",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "TRANSPORT implementation authorization decision recorded. "
                "Seven locked constants sealed: LP solver variant, pivot rule, "
                "tie-breaking strategy, balance tolerance, max problem size, "
                "cost matrix magnitude bound, NOT_COMPUTABLE branch enumeration. "
                "Operator opens implementation PR constrained to TEST_VECTOR_COMPUTATION_ONLY "
                "lane and SHADOW_STUB_ONLY baseline. "
                "No self-authorizing advancement step exists."
            ),
        },
        {
            "rank": 3,
            "option_id": "N_RANK6_OPERATOR_SELECTION",
            "option_name": "Rank-6 metric operator selection",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Operator designates rank-6 operator from remaining 7 NOT_IMPLEMENTED "
                "operators. May proceed in parallel with TRANSPORT implementation gate. "
                "Requires explicit operator designation."
            ),
        },
        {
            "rank": 4,
            "option_id": "M_REGISTRY_HARDENING",
            "option_name": "Registry hardening",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Emit MetricOperatorRegistryStabilization update reflecting "
                "TRANSPORT implementation authorization decision recorded status. "
                "Advisory only; does not authorize implementation."
            ),
        },
        {
            "rank": 5,
            "option_id": "C_METRIC_EMISSION_AUTHORIZATION_REVIEW",
            "option_name": "Metric emission authorization review",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful without separate operator-authorized governance design. "
                "No CPU reference implementation exists for any operator. "
                "Premature without at least one operator implementation authorization first."
            ),
        },
        {
            "rank": 6,
            "option_id": "E_P43_SURFACE_LANE_READINESS",
            "option_name": "P43 surface lane readiness",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. Explicitly blocked by current operator instruction. "
                "Requires separate operator-authorized governance design."
            ),
        },
    ]


def four_operator_post_norm_geometry_ranked_options() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "option_id": "G_SEALED_PAUSE",
            "option_name": "Sealed pause / no-op",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": False,
            "first_lawful_step": None,
        },
        {
            "rank": 2,
            "option_id": "K_TRANSPORT_IMPLEMENTATION_AUTHORIZATION",
            "option_name": "TRANSPORT implementation authorization prep and gate path",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "TRANSPORT CPU baseline planning is complete. "
                "Operator emits explicit TRANSPORT implementation authorization instruction "
                "with seven locked constants: LP solver variant, pivot rule, "
                "tie-breaking strategy, balance tolerance (epsilon_rel), "
                "max problem size (m*n), cost matrix magnitude bound, and "
                "NOT_COMPUTABLE branch enumeration confirmation. "
                "Advisory only. No self-authorizing step exists."
            ),
        },
        {
            "rank": 3,
            "option_id": "N_RANK6_OPERATOR_SELECTION",
            "option_name": "Rank-6 metric operator selection",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Operator designates rank-6 operator from remaining 7 NOT_IMPLEMENTED "
                "operators. May proceed in parallel with TRANSPORT authorization gate path. "
                "Requires explicit operator designation."
            ),
        },
        {
            "rank": 4,
            "option_id": "M_REGISTRY_HARDENING",
            "option_name": "Registry hardening",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Emit MetricOperatorRegistryStabilization update reflecting four-operator "
                "SHADOW_STUB_ONLY parity and TRANSPORT CPU_BASELINE_PLANNING_COMPLETE status. "
                "Advisory only; does not authorize implementation."
            ),
        },
        {
            "rank": 5,
            "option_id": "C_METRIC_EMISSION_AUTHORIZATION_REVIEW",
            "option_name": "Metric emission authorization review",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful without separate operator-authorized governance design. "
                "No CPU reference implementation exists for any operator. "
                "Premature without at least one operator implementation authorization first."
            ),
        },
        {
            "rank": 6,
            "option_id": "E_P43_SURFACE_LANE_READINESS",
            "option_name": "P43 surface lane readiness",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. Explicitly blocked by current operator instruction. "
                "Requires separate operator-authorized governance design."
            ),
        },
    ]


def authorization_prep_complete_ranked_options() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "option_id": "G_SEALED_PAUSE",
            "option_name": "Sealed pause / no-op",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": False,
            "first_lawful_step": None,
        },
        {
            "rank": 2,
            "option_id": "J_NORM_GEOMETRY_IMPLEMENTATION_AUTHORIZATION",
            "option_name": "NORM_GEOMETRY implementation authorization",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "ImplementationAuthorizationPrep.v1 recommends NORM_GEOMETRY as "
                "first implementation path: closed-form Lp norm, no LP solver "
                "dependency, lower numerical risk, smaller test surface. "
                "Operator emits explicit authorization instruction with five "
                "locked constants: float64 precision declaration, p_inf sentinel "
                "value, max element magnitude, max p value, NOT_COMPUTABLE "
                "branch enumeration confirmation."
            ),
        },
        {
            "rank": 3,
            "option_id": "K_TRANSPORT_IMPLEMENTATION_AUTHORIZATION",
            "option_name": "TRANSPORT implementation authorization",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Blocked pending seven locked constants: LP solver variant, "
                "pivot rule, tie-breaking strategy, balance tolerance "
                "(epsilon_rel), max problem size (m*n), cost matrix magnitude "
                "bound, and NOT_COMPUTABLE branch enumeration confirmation. "
                "All seven must be declared before any TRANSPORT implementation "
                "PR may be opened."
            ),
        },
        {
            "rank": 4,
            "option_id": "L_RANK6_OPERATOR_SELECTION",
            "option_name": "Rank-6 metric operator selection",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Operator designates rank-6 operator from remaining 7 "
                "NOT_IMPLEMENTED operators. Lower priority than NORM_GEOMETRY "
                "and TRANSPORT implementation authorizations; may proceed "
                "in parallel with implementation planning."
            ),
        },
        {
            "rank": 5,
            "option_id": "M_REGISTRY_HARDENING",
            "option_name": "Registry hardening",
            "authority_posture": "ADVISORY_ONLY",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Emit MetricOperatorRegistryStabilization update reflecting "
                "NORM_GEOMETRY and TRANSPORT at CPU_BASELINE_PLANNING_COMPLETE "
                "status. Advisory-only; does not authorize implementation."
            ),
        },
        {
            "rank": 6,
            "option_id": "C_METRIC_EMISSION_AUTHORIZATION_REVIEW",
            "option_name": "Metric emission authorization review",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful without separate operator-authorized governance design. "
                "No CPU reference implementation exists for any operator. "
                "Premature without at least one operator implementation "
                "authorization first."
            ),
        },
        {
            "rank": 7,
            "option_id": "E_P43_SURFACE_LANE_READINESS",
            "option_name": "P43 surface lane readiness",
            "authority_posture": "BLOCKED",
            "requires_operator_instruction": True,
            "first_lawful_step": (
                "Not lawful. Explicitly blocked by current operator instruction. "
                "Requires separate operator-authorized governance design."
            ),
        },
    ]


def _assert_provenance_safe(value: Any) -> None:
    if isinstance(value, dict):
        for v in value.values():
            _assert_provenance_safe(v)
        return
    if isinstance(value, list):
        for v in value:
            _assert_provenance_safe(v)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if any(token in lowered for token in FORBIDDEN_PROVENANCE_TOKENS):
            raise MetricOperatorFrontierRecommendationError(
                "forbidden_provenance_reference_detected"
            )


def validate_metric_operator_frontier_recommendation(rec: dict[str, Any]) -> None:
    required = {
        "schema_version", "recommendation_id", "recommendation_status", "ranked_options",
        "recommended_next_step", "required_operator_decision", "stop_boundary_reason",
        "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - rec.keys())
    if missing:
        raise MetricOperatorFrontierRecommendationError(f"missing_required_fields:{missing}")

    if rec["schema_version"] != SCHEMA_VERSION:
        raise MetricOperatorFrontierRecommendationError("invalid_schema_version")

    if rec["recommendation_status"] not in ALLOWED_RECOMMENDATION_STATUS:
        raise MetricOperatorFrontierRecommendationError(
            f"invalid_recommendation_status:{rec['recommendation_status']}"
        )

    options = rec["ranked_options"]
    if not options:
        raise MetricOperatorFrontierRecommendationError("ranked_options_must_be_non_empty")

    ranks_seen: set[int] = set()
    ids_seen: set[str] = set()
    for opt in options:
        r = opt.get("rank")
        if r in ranks_seen:
            raise MetricOperatorFrontierRecommendationError(f"duplicate_rank:{r}")
        ranks_seen.add(r)
        oid = opt.get("option_id", "")
        if oid in ids_seen:
            raise MetricOperatorFrontierRecommendationError(f"duplicate_option_id:{oid}")
        ids_seen.add(oid)
        if opt.get("authority_posture") not in ALLOWED_AUTHORITY_POSTURE:
            raise MetricOperatorFrontierRecommendationError(
                f"invalid_authority_posture:{opt.get('authority_posture')}"
            )

    if rec["output_contract"] != default_output_contract():
        raise MetricOperatorFrontierRecommendationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if rec["governance_flags"].get(flag) is not False:
            raise MetricOperatorFrontierRecommendationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(rec["provenance"])


def compute_metric_operator_frontier_recommendation_hash(rec: dict[str, Any]) -> str:
    return canonical_hash(_preimage(rec))


def serialize_metric_operator_frontier_recommendation(rec: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(rec)) + "\n"


def build_metric_operator_frontier_recommendation(payload: dict[str, Any]) -> dict[str, Any]:
    options = sorted(
        payload.get("ranked_options", []),
        key=lambda o: o["rank"],
    )
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "ranked_options": options,
    }
    base["canonical_hash"] = compute_metric_operator_frontier_recommendation_hash(base)
    validate_metric_operator_frontier_recommendation(base)
    return _finalize(base)
