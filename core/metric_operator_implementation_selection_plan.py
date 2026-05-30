from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricOperatorImplementationSelectionPlan.v1"
PLAN_TYPE = "METRIC_OPERATOR_IMPLEMENTATION_SELECTION_PLAN"

ALLOWED_SELECTION_FAMILIES = (
    "FIRST_OPERATOR_SELECTION",
    "BASELINE_OPERATOR_SELECTION",
    "LOW_RISK_OPERATOR_SELECTION",
    "PROJECTION_READY_OPERATOR_SELECTION",
    "MULTI_OPERATOR_SELECTION_PLANNING",
)
ALLOWED_INTENDED_LANES = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_SELECTION_STAGES = (
    "SELECTION_PLAN_ONLY",
    "READINESS_RANKING_ONLY",
    "IMPLEMENTATION_NOT_STARTED",
    "BLOCKED_PENDING_OPERATOR_REVIEW",
)
ALLOWED_OPERATOR_IDS = (
    "WASSERSTEIN",
    "CHAMFER_DISTANCE",
    "GEODESIC",
    "NORM_GEOMETRY",
    "TRANSPORT",
    "HYPERVECTOR_BINDING",
    "RESERVOIR_STATE_SPACE",
    "COUNTERFACTUAL_DIFFUSION",
    "HEAVY_TAIL",
    "HYSTERESIS",
    "STOCHASTIC_GEOMETRY",
    "TOPOLOGICAL_PRIMITIVES",
)
ALLOWED_OPERATOR_FAMILIES = (
    "TRANSPORT_METRIC",
    "SPATIAL_ALIGNMENT",
    "GEODESIC_TOPOLOGY",
    "NORM_GEOMETRY",
    "SYMBOLIC_BINDING",
    "STATE_SPACE_DIAGNOSTIC",
    "COUNTERFACTUAL_GEOMETRY",
    "DISTRIBUTION_TAIL_ANALYSIS",
    "PATH_DEPENDENT_MEMORY",
    "STOCHASTIC_SPATIAL_FIELD",
    "TOPOLOGICAL_FEATURE_EXTRACTION",
)
ALLOWED_READINESS_STATUS = (
    "READY_FOR_IMPLEMENTATION_PLAN",
    "NEEDS_MORE_TEST_VECTORS",
    "NEEDS_BASELINE_COMPARATOR",
    "NEEDS_OPERATOR_REVIEW",
    "BLOCKED_BY_GOVERNANCE",
    "NOT_COMPUTABLE",
)
ALLOWED_IMPLEMENTATION_RISK = ("LOW", "MEDIUM", "HIGH", "NOT_COMPUTABLE")
ALLOWED_IMPLEMENTATION_STATUS = (
    "SELECTED_FOR_PLANNING_ONLY",
    "CANDIDATE_ONLY",
    "NOT_IMPLEMENTED",
    "BLOCKED_PENDING_REVIEW",
)
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
)
FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast", "scoring", "metric-computation", "metric-value",
)


class MetricOperatorImplementationSelectionPlanValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_operator_candidates() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "cand-001-wasserstein",
            "operator_id": "WASSERSTEIN",
            "operator_family": "TRANSPORT_METRIC",
            "selection_rank": 1,
            "readiness_status": "NEEDS_OPERATOR_REVIEW",
            "implementation_risk": "MEDIUM",
            "evidence_refs": [
                "MetricOperatorRegistry.v1:registry-001",
                "MetricOperatorBaselineTestVectorPack.v1:pack-001",
                "AALVizGeometricRendererImplementationPlan.v1:plan-001",
            ],
            "blocked_operations": ["metric_math_implementation", "score_computation", "runtime_mutation"],
            "rationale": "First-candidate planning selection metadata only; implementation remains blocked.",
            "implementation_status": "SELECTED_FOR_PLANNING_ONLY",
        }
    ]


def default_selection_policy() -> dict[str, bool]:
    return {
        "uses_test_vectors": True,
        "uses_registry_metadata": True,
        "uses_renderer_plan_context": True,
        "no_metric_computation": True,
        "no_runtime_effect": True,
        "no_forecast_effect": True,
        "no_authority_grant": True,
    }


def default_readiness_constraints() -> dict[str, bool]:
    return {
        "requires_test_vector_coverage": True,
        "requires_baseline_comparator": True,
        "requires_operator_review": True,
        "requires_no_authority_scan": True,
        "requires_no_runtime_mutation": True,
        "requires_no_forecast_influence": True,
    }


def default_implementation_gates() -> dict[str, bool]:
    return {
        "implementation_blocked": True,
        "planning_only": True,
        "requires_new_operator_plan": True,
        "requires_dedicated_tests": True,
        "requires_stabilization_window": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_code": False,
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_selection_metadata": True,
        "emits_readiness_ranking": True,
    }


def _assert_provenance_safe(value: Any) -> None:
    if isinstance(value, dict):
        for v in value.values():
            _assert_provenance_safe(v)
    elif isinstance(value, list):
        for v in value:
            _assert_provenance_safe(v)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(token in lowered for token in FORBIDDEN_PROVENANCE_TOKENS):
            raise MetricOperatorImplementationSelectionPlanValidationError("forbidden_provenance_reference_detected")


def validate_metric_operator_implementation_selection_plan(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "plan_id", "plan_type", "source_metric_registry_refs", "source_test_vector_pack_refs",
        "source_renderer_implementation_plan_refs", "selection_scope", "operator_candidates", "selection_policy",
        "readiness_constraints", "implementation_gates", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise MetricOperatorImplementationSelectionPlanValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise MetricOperatorImplementationSelectionPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise MetricOperatorImplementationSelectionPlanValidationError("invalid_plan_type")

    scope = packet["selection_scope"]
    if scope.get("selection_family") not in ALLOWED_SELECTION_FAMILIES:
        raise MetricOperatorImplementationSelectionPlanValidationError("unknown_selection_family")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANES:
        raise MetricOperatorImplementationSelectionPlanValidationError("unknown_intended_lane")
    if scope.get("selection_stage") not in ALLOWED_SELECTION_STAGES:
        raise MetricOperatorImplementationSelectionPlanValidationError("unknown_selection_stage")

    candidates = packet["operator_candidates"]
    if not candidates:
        raise MetricOperatorImplementationSelectionPlanValidationError("operator_candidates_must_be_non_empty")

    seen: set[str] = set()
    for candidate in sorted(candidates, key=lambda x: (x["selection_rank"], x["candidate_id"])):
        cid = candidate["candidate_id"]
        if cid in seen:
            raise MetricOperatorImplementationSelectionPlanValidationError("duplicate_candidate_id")
        seen.add(cid)
        if candidate["operator_id"] not in ALLOWED_OPERATOR_IDS:
            raise MetricOperatorImplementationSelectionPlanValidationError("unknown_operator_id")
        if candidate["operator_family"] not in ALLOWED_OPERATOR_FAMILIES:
            raise MetricOperatorImplementationSelectionPlanValidationError("unknown_operator_family")
        if candidate["readiness_status"] not in ALLOWED_READINESS_STATUS:
            raise MetricOperatorImplementationSelectionPlanValidationError("unknown_readiness_status")
        if candidate["implementation_risk"] not in ALLOWED_IMPLEMENTATION_RISK:
            raise MetricOperatorImplementationSelectionPlanValidationError("unknown_implementation_risk")
        if candidate["implementation_status"] not in ALLOWED_IMPLEMENTATION_STATUS:
            raise MetricOperatorImplementationSelectionPlanValidationError("unknown_implementation_status")
        if not isinstance(candidate["selection_rank"], int) or candidate["selection_rank"] <= 0:
            raise MetricOperatorImplementationSelectionPlanValidationError("invalid_selection_rank")

    if packet["selection_policy"] != default_selection_policy():
        raise MetricOperatorImplementationSelectionPlanValidationError("invalid_selection_policy")
    if packet["readiness_constraints"] != default_readiness_constraints():
        raise MetricOperatorImplementationSelectionPlanValidationError("invalid_readiness_constraints")
    if packet["implementation_gates"] != default_implementation_gates():
        raise MetricOperatorImplementationSelectionPlanValidationError("invalid_implementation_gates")
    if packet["output_contract"] != default_output_contract():
        raise MetricOperatorImplementationSelectionPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise MetricOperatorImplementationSelectionPlanValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(packet["provenance"])


def compute_metric_operator_implementation_selection_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_metric_operator_implementation_selection_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_metric_operator_implementation_selection_plan(payload: dict[str, Any]) -> dict[str, Any]:
    candidates = sorted(payload.get("operator_candidates", default_operator_candidates()), key=lambda x: (x["selection_rank"], x["candidate_id"]))
    for candidate in candidates:
        candidate["evidence_refs"] = sorted(candidate.get("evidence_refs", []))
        candidate["blocked_operations"] = sorted(candidate.get("blocked_operations", []))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "source_test_vector_pack_refs": sorted(payload.get("source_test_vector_pack_refs", [])),
        "source_renderer_implementation_plan_refs": sorted(payload.get("source_renderer_implementation_plan_refs", [])),
        "operator_candidates": candidates,
        "selection_policy": payload.get("selection_policy", default_selection_policy()),
        "readiness_constraints": payload.get("readiness_constraints", default_readiness_constraints()),
        "implementation_gates": payload.get("implementation_gates", default_implementation_gates()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_metric_operator_implementation_selection_plan_hash(base)
    validate_metric_operator_implementation_selection_plan(base)
    return _finalize(base)
