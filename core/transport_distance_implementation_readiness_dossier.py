from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportDistanceImplementationReadinessDossier.v1"
DOSSIER_TYPE = "TRANSPORT_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER"
OPERATOR_ID = "TRANSPORT"
INTENDED_LANE = "SHADOW"
READINESS_SCOPE = "IMPLEMENTATION_READINESS_ONLY"
DOSSIER_STATUS = "TRANSPORT_READINESS_DOSSIER_DEFINED"

REQUIRED_BLOCKED_SCOPES: frozenset[str] = frozenset({
    "transport_computation",
    "lp_solver_invocation",
    "emits_metric_values",
    "forecast_influence",
    "p43_surface_lanes",
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "execution_authority",
    "inference_authority",
})

LOCKED_TRUE_AUTHORITY_KEYS = (
    "advisory_only",
    "shadow_lane_only",
    "readiness_dossier_only",
)
LOCKED_FALSE_AUTHORITY_KEYS = (
    "transport_computation_authorized",
    "lp_solver_invocation_authorized",
    "emits_metric_values",
    "forecast_influence",
    "p43_surface_lanes_authorized",
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "execution_authority",
    "inference_authority",
)
LOCKED_FALSE_GOVERNANCE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation",
    "runtime_authority", "runtime_mutation", "forecast_influence",
    "execution_authority", "token_minting_allowed", "valid_for_execution",
    "activation_approved", "authorization_granted",
)
FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast",
    "scoring", "metric-computation", "metric-value", "geodesic-distance",
    "numpy", "scipy", "gpu-kernel",
)


class TransportDistanceImplementationReadinessDossierValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_output_contract() -> dict[str, bool]:
    return {
        "implementation_completed": False,
        "runtime_enabled": False,
        "scheduler_enabled": False,
        "renderer_enabled": False,
        "oracle_enabled": False,
        "forecast_enabled": False,
        "production_ready": False,
    }


def default_authority_locks() -> dict[str, bool]:
    locks: dict[str, bool] = {}
    for k in LOCKED_TRUE_AUTHORITY_KEYS:
        locks[k] = True
    for k in LOCKED_FALSE_AUTHORITY_KEYS:
        locks[k] = False
    return locks


def default_mathematical_requirements() -> list[str]:
    return [
        "The discrete transport distance is defined over a finite set of source "
        "nodes with supply vector s ∈ R^m_+ and a finite set of target nodes with "
        "demand vector d ∈ R^n_+, paired with a cost matrix C ∈ R^{m×n}_+.",
        "Balanced transport constraint: sum(s) must equal sum(d) to a tolerance "
        "of float64 epsilon; unbalanced inputs must route to NOT_COMPUTABLE.",
        "The transport plan T ∈ R^{m×n}_+ minimizes the total cost "
        "sum_{i,j} C[i,j] * T[i,j] subject to the row marginal constraint "
        "T @ 1_n = s and the column marginal constraint T^T @ 1_m = d.",
        "For the single-source degenerate case (m=1): T[0,j] = d[j] for all j; "
        "the transport distance is sum_j C[0,j] * d[j] with no LP required.",
        "For the single-target degenerate case (n=1): T[i,0] = s[i] for all i; "
        "the transport distance is sum_i C[i,0] * s[i] with no LP required.",
        "For the 1x1 degenerate case: transport distance equals C[0,0] * s[0] "
        "when s[0] == d[0]; otherwise NOT_COMPUTABLE.",
        "When the cost matrix C is a valid metric distance matrix and supply/demand "
        "are probability simplices, the transport distance equals the discrete "
        "Wasserstein-1 distance with that ground metric.",
        "All supply, demand, and cost values must be finite, non-negative float64; "
        "negative or non-finite values must route to NOT_COMPUTABLE.",
    ]


def default_input_shape_requirements() -> list[str]:
    return [
        "Supply vector s must be a non-empty sequence of non-negative finite float64 "
        "values; empty supply (m=0) must route to NOT_COMPUTABLE.",
        "Demand vector d must be a non-empty sequence of non-negative finite float64 "
        "values; empty demand (n=0) must route to NOT_COMPUTABLE.",
        "Cost matrix C must have shape (m, n) where m = len(s) and n = len(d); "
        "shape mismatch must route to NOT_COMPUTABLE.",
        "All elements of C must be non-negative finite float64; negative or non-finite "
        "cost values must route to NOT_COMPUTABLE.",
        "sum(s) must equal sum(d) to within float64 relative epsilon; unbalanced "
        "transport must route to NOT_COMPUTABLE.",
        "Non-finite values (NaN, +Inf, -Inf) in s, d, or C must route to "
        "NOT_COMPUTABLE without any transport distance computation.",
        "Negative values in s or d (individual supply/demand < 0) must route to "
        "NOT_COMPUTABLE even if the overall sum is non-negative.",
    ]


def default_determinism_requirements() -> list[str]:
    return [
        "For degenerate cases (m=1 or n=1) the transport distance is a closed-form "
        "weighted sum; it is fully deterministic given identical float64 inputs.",
        "For general m x n balanced transport, the LP solver must be configured with "
        "a fixed pivot rule and declared traversal order so that equivalent problems "
        "always produce the same optimal transport plan.",
        "The implementation plan must declare the LP solver variant, pivoting strategy, "
        "and tie-breaking rule before any implementation begins.",
        "No randomized or probabilistic algorithm components are permitted in the "
        "baseline deterministic plan; stochastic LP variants are out of scope.",
        "All transport distance computations must produce identical results across "
        "independent runs given identical inputs and an identical declared solver "
        "configuration.",
    ]


def default_numerical_constraints() -> list[str]:
    return [
        "Float64 precision required for all intermediate computations including "
        "cost accumulation, marginal constraint checking, and supply/demand balance.",
        "Float32 is excluded from the baseline plan.",
        "The balance check sum(s) == sum(d) must be performed in float64; "
        "the tolerance must be declared (e.g., relative epsilon 1e-9) before "
        "the implementation plan is finalized.",
        "For large m or n, accumulated cost may approach float64 overflow bounds; "
        "the implementation plan must declare a bound on m, n, and cost values.",
        "No transport distance computation of any kind is permitted during the "
        "planning phase.",
    ]


def default_numerical_stability_requirements() -> list[str]:
    return [
        "For degenerate m=1 or n=1 cases, cost accumulation uses left-to-right "
        "summation in declared index order; no reordering is permitted.",
        "For general LP: dual variables (shadow prices) must be computed in float64 "
        "throughout; no intermediate float32 representation.",
        "Degenerate LP solutions (multiple optimal transport plans) must be handled "
        "by a declared tie-breaking rule before implementation; the tie-breaking "
        "rule must be deterministic.",
        "Zero-supply or zero-demand individual nodes (s[i]=0 or d[j]=0) are valid "
        "inputs; the implementation must handle zero-weight marginals without "
        "division by zero.",
        "Very small positive supply/demand values (near float64 min positive) must "
        "not underflow to 0.0 in intermediate summations; a documented minimum "
        "value policy is required before implementation.",
    ]


def default_dependency_inventory() -> list[dict[str, Any]]:
    return [
        {
            "dependency_id": "dep_001_test_vector_pack",
            "dependency_type": "TEST_VECTOR",
            "description": (
                "Transport distance baseline test vector from the metric operator "
                "baseline test vector pack; currently VALID_METADATA_VECTOR only; "
                "expected transport distance fields not yet added."
            ),
            "status": "NOT_READY",
            "blocking": True,
        },
        {
            "dependency_id": "dep_002_lp_solver_convention",
            "dependency_type": "SOLVER_POLICY",
            "description": (
                "The LP solver variant, pivot rule, and tie-breaking strategy must "
                "be declared before the test vector schema can be finalized. "
                "The baseline plan uses a fixed pivot rule for determinism."
            ),
            "status": "PLANNED_ONLY",
            "blocking": True,
        },
        {
            "dependency_id": "dep_003_balance_tolerance",
            "dependency_type": "NUMERICAL_POLICY",
            "description": (
                "The supply-demand balance tolerance (relative epsilon for "
                "sum(s) == sum(d)) must be declared before fixture schema "
                "can be finalized."
            ),
            "status": "PLANNED_ONLY",
            "blocking": True,
        },
        {
            "dependency_id": "dep_004_cost_matrix_representation",
            "dependency_type": "DATA_LAYOUT",
            "description": (
                "The canonical cost matrix representation format (JSON array of "
                "arrays of float64 values, row-major) must be declared before "
                "fixture schema can be defined."
            ),
            "status": "PLANNED_ONLY",
            "blocking": True,
        },
    ]


def default_implementation_prerequisites() -> list[dict[str, Any]]:
    return [
        {
            "description": (
                "MetricOperatorRank5SelectionPlan.v1 must be present selecting "
                "TRANSPORT at rank 5 with SELECTION_PLAN_ONLY scope."
            ),
            "evidence_refs": [
                "MetricOperatorRank5SelectionPlan.v1:metric_operator_rank5_selection_plan_001"
            ],
            "prereq_status": "REQUIRED",
        },
        {
            "description": (
                "MetricOperatorRank5CandidateAudit.v1 must be present confirming "
                "TRANSPORT as the rank-5 candidate."
            ),
            "evidence_refs": [
                "MetricOperatorRank5CandidateAudit.v1:metric_operator_rank5_candidate_audit_001"
            ],
            "prereq_status": "REQUIRED",
        },
        {
            "description": (
                "TransportTestVectorSchemaPlan.v1 must be completed before "
                "fixture schema definitions can be created."
            ),
            "evidence_refs": [],
            "prereq_status": "DEFERRED",
        },
        {
            "description": (
                "LP solver policy (solver variant, pivot rule, tie-breaking) must be "
                "declared in the implementation plan before any LP-dependent "
                "fixture values can be pinned."
            ),
            "evidence_refs": [],
            "prereq_status": "DEFERRED",
        },
    ]


def default_implementation_risks() -> list[dict[str, Any]]:
    return [
        {
            "description": (
                "LP solver non-determinism for degenerate problems (multiple "
                "optimal transport plans): different pivot rules may yield "
                "different optimal T with the same objective value."
            ),
            "risk_level": "MEDIUM",
            "mitigation": (
                "Declare a fixed, deterministic pivot rule and tie-breaking "
                "convention in the implementation plan; restrict test fixtures "
                "to problems with unique optimal transport plans until the "
                "tie-breaking policy is locked."
            ),
        },
        {
            "description": (
                "Supply-demand balance floating-point drift: float64 summation "
                "of non-trivial supply/demand vectors may produce sum(s) != sum(d) "
                "at machine epsilon, triggering spurious NOT_COMPUTABLE."
            ),
            "risk_level": "MEDIUM",
            "mitigation": (
                "Declare a relative balance tolerance (e.g., 1e-9) in the "
                "implementation plan; test fixtures must include a case "
                "near the tolerance boundary."
            ),
        },
        {
            "description": (
                "Degenerate zero-supply/demand nodes: a supply or demand node "
                "with value 0.0 must not trigger division-by-zero in marginal "
                "constraint checking."
            ),
            "risk_level": "LOW",
            "mitigation": (
                "Add a dedicated NOT_COMPUTABLE or zero-marginal handling branch "
                "in the implementation plan; include a test fixture with a "
                "zero-supply node."
            ),
        },
        {
            "description": (
                "Cost matrix size bounds: for large m, n, the LP has m*n "
                "variables; unbounded m and n may cause memory exhaustion."
            ),
            "risk_level": "LOW",
            "mitigation": (
                "Declare maximum allowed m and n in the implementation plan; "
                "add NOT_COMPUTABLE branch for oversized inputs."
            ),
        },
    ]


def default_validation_requirements() -> list[dict[str, Any]]:
    return [
        {
            "description": (
                "Baseline test vectors must be extended with transport-specific "
                "reference inputs (supply vector, demand vector, cost matrix) and "
                "pinned expected transport distance scalars before implementation begins."
            ),
            "validation_type": "REFERENCE_VECTOR",
            "evidence_refs": [],
        },
        {
            "description": (
                "NOT_COMPUTABLE cases (unbalanced supply/demand, negative supply, "
                "negative demand, negative cost, empty supply, empty demand, "
                "non-finite values) must each have a dedicated validation fixture."
            ),
            "validation_type": "EDGE_CASE_VALIDATION",
            "evidence_refs": [],
        },
        {
            "description": (
                "Deterministic replay validation: identical supply, demand, and "
                "cost matrix inputs must produce identical transport distance "
                "output across independent runs."
            ),
            "validation_type": "DETERMINISTIC_REPLAY",
            "evidence_refs": [],
        },
        {
            "description": (
                "Float64 precision validation: all intermediate computations must "
                "use float64; no float32 intermediate values permitted."
            ),
            "validation_type": "NUMERICAL_STABILITY",
            "evidence_refs": [],
        },
        {
            "description": (
                "Degenerate case validation: m=1 (single source) and n=1 "
                "(single target) must each have dedicated fixtures with "
                "analytically exact expected transport distance values."
            ),
            "validation_type": "SPECIAL_CASE_VALIDATION",
            "evidence_refs": [],
        },
    ]


def default_blocked_scopes() -> list[str]:
    return sorted(REQUIRED_BLOCKED_SCOPES)


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportDistanceImplementationReadinessDossierValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_transport_distance_implementation_readiness_dossier(
    packet: dict[str, Any],
) -> None:
    req = {
        "schema_version", "dossier_id", "dossier_type", "selected_operator",
        "dossier_status", "readiness_scope", "intended_lane", "implementation_scope",
        "mathematical_requirements", "input_shape_requirements",
        "determinism_requirements", "numerical_constraints",
        "numerical_stability_requirements", "dependency_inventory",
        "implementation_prerequisites", "implementation_risks",
        "validation_requirements", "blocked_scopes", "authority_locks",
        "output_contract", "governance_flags", "provenance", "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise TransportDistanceImplementationReadinessDossierValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise TransportDistanceImplementationReadinessDossierValidationError(
            "invalid_schema_version"
        )
    if packet["dossier_type"] != DOSSIER_TYPE:
        raise TransportDistanceImplementationReadinessDossierValidationError(
            "invalid_dossier_type"
        )
    if packet["selected_operator"] != OPERATOR_ID:
        raise TransportDistanceImplementationReadinessDossierValidationError(
            "unknown_selected_operator"
        )
    if packet["dossier_status"] != DOSSIER_STATUS:
        raise TransportDistanceImplementationReadinessDossierValidationError(
            "invalid_dossier_status"
        )
    if packet["readiness_scope"] != READINESS_SCOPE:
        raise TransportDistanceImplementationReadinessDossierValidationError(
            "invalid_readiness_scope"
        )
    if packet["intended_lane"] != INTENDED_LANE:
        raise TransportDistanceImplementationReadinessDossierValidationError(
            "invalid_intended_lane"
        )

    blocked = set(packet.get("blocked_scopes", []))
    missing_scopes = REQUIRED_BLOCKED_SCOPES - blocked
    if missing_scopes:
        raise TransportDistanceImplementationReadinessDossierValidationError(
            f"missing_required_blocked_scopes:{sorted(missing_scopes)}"
        )

    locks = packet["authority_locks"]
    for k in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(k) is not True:
            raise TransportDistanceImplementationReadinessDossierValidationError(
                f"authority_lock_must_be_true:{k}"
            )
    for k in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(k) is not False:
            raise TransportDistanceImplementationReadinessDossierValidationError(
                f"authority_lock_must_be_false:{k}"
            )

    if packet["output_contract"] != default_output_contract():
        raise TransportDistanceImplementationReadinessDossierValidationError(
            "invalid_output_contract"
        )

    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise TransportDistanceImplementationReadinessDossierValidationError(
                f"governance_flag_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_transport_distance_implementation_readiness_dossier_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_transport_distance_implementation_readiness_dossier(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_transport_distance_implementation_readiness_dossier(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "dossier_type": DOSSIER_TYPE,
        "selected_operator": OPERATOR_ID,
        "dossier_status": DOSSIER_STATUS,
        "readiness_scope": READINESS_SCOPE,
        "intended_lane": INTENDED_LANE,
        "mathematical_requirements": payload.get(
            "mathematical_requirements", default_mathematical_requirements()
        ),
        "input_shape_requirements": payload.get(
            "input_shape_requirements", default_input_shape_requirements()
        ),
        "determinism_requirements": payload.get(
            "determinism_requirements", default_determinism_requirements()
        ),
        "numerical_constraints": payload.get(
            "numerical_constraints", default_numerical_constraints()
        ),
        "numerical_stability_requirements": payload.get(
            "numerical_stability_requirements", default_numerical_stability_requirements()
        ),
        "dependency_inventory": payload.get(
            "dependency_inventory", default_dependency_inventory()
        ),
        "implementation_prerequisites": payload.get(
            "implementation_prerequisites", default_implementation_prerequisites()
        ),
        "implementation_risks": payload.get(
            "implementation_risks", default_implementation_risks()
        ),
        "validation_requirements": payload.get(
            "validation_requirements", default_validation_requirements()
        ),
        "blocked_scopes": sorted(
            payload.get("blocked_scopes", default_blocked_scopes())
        ),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = (
        compute_transport_distance_implementation_readiness_dossier_hash(base)
    )
    validate_transport_distance_implementation_readiness_dossier(base)
    return _finalize(base)
