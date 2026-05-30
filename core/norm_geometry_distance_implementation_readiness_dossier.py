from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryDistanceImplementationReadinessDossier.v1"
DOSSIER_TYPE = "NORM_GEOMETRY_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER"
OPERATOR_ID = "NORM_GEOMETRY"
INTENDED_LANE = "SHADOW"
READINESS_SCOPE = "IMPLEMENTATION_READINESS_ONLY"
DOSSIER_STATUS = "NORM_GEOMETRY_READINESS_DOSSIER_DEFINED"

REQUIRED_BLOCKED_SCOPES: frozenset[str] = frozenset({
    "norm_geometry_computation",
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
    "norm_geometry_computation_authorized",
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


class NormGeometryDistanceImplementationReadinessDossierValidationError(ValueError):
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
        "The Lp norm distance between vectors x and y in R^n is defined as "
        "||x - y||_p = (sum_i |x_i - y_i|^p)^(1/p) for p >= 1.",
        "Special case p=1 (L1, Manhattan distance): ||x - y||_1 = sum_i |x_i - y_i|. "
        "Exact integer arithmetic is possible for integer-valued inputs; float64 "
        "required for the general case.",
        "Special case p=2 (L2, Euclidean distance): ||x - y||_2 = sqrt(sum_i (x_i - y_i)^2). "
        "Float64 required; square root must use a stable float64 implementation.",
        "Special case p=inf (Chebyshev distance): ||x - y||_inf = max_i |x_i - y_i|. "
        "Exact over float64 without a power or root operation.",
        "For general p: the power operation (|x_i - y_i|^p) must use float64 "
        "throughout; no float32 intermediate values are permitted.",
        "Vectors must have equal length (dimension n >= 1). "
        "Mismatched lengths are an invalid input and must be rejected before "
        "any distance computation begins.",
        "Zero vector inputs (all elements 0.0) are valid; the distance between "
        "two identical zero vectors is 0.0.",
        "The p parameter must satisfy p >= 1; values below 1.0 do not define "
        "a proper norm and must route to NOT_COMPUTABLE.",
    ]


def default_input_shape_requirements() -> list[str]:
    return [
        "Both input vectors (x and y) must be declared as finite, equal-length "
        "sequences of float64 values.",
        "The dimension n must be >= 1; empty vector inputs (n = 0) must route "
        "to NOT_COMPUTABLE.",
        "The p parameter must be a float64 value >= 1.0; values < 1.0 must route "
        "to NOT_COMPUTABLE.",
        "Non-finite float64 values (NaN, +Inf, -Inf) in either vector must route "
        "to NOT_COMPUTABLE without distance computation.",
        "Mismatched vector lengths (len(x) != len(y)) must route to NOT_COMPUTABLE.",
        "Integer-valued vector inputs must be promoted to float64 before computation.",
        "The p=inf case must be declared explicitly or inferred from a sentinel "
        "value; the implementation plan must declare which convention is used.",
    ]


def default_determinism_requirements() -> list[str]:
    return [
        "Lp norm distance is a closed-form expression with no iterative solver; "
        "it is fully deterministic given identical float64 vector inputs and an "
        "identical p parameter.",
        "All element-wise absolute difference and power operations must be applied "
        "in a declared, stable traversal order (e.g., index 0 to n-1).",
        "The summation order must be documented and fixed; the canonical order is "
        "left-to-right (index 0 to n-1).",
        "No randomized or probabilistic algorithm components are permitted "
        "in the baseline plan.",
        "All Lp norm computations must produce identical results across independent "
        "runs given identical inputs.",
    ]


def default_numerical_constraints() -> list[str]:
    return [
        "Float64 precision required for all intermediate computations including "
        "element-wise differences, powers, summation, and root extraction.",
        "Float32 is excluded from the baseline plan.",
        "Overflow risk: for large p values and large vector elements, "
        "|x_i - y_i|^p may overflow float64; the implementation plan must "
        "declare a bound on p and element magnitudes before implementation.",
        "Underflow risk: for small differences and large p, individual terms "
        "may underflow to 0.0 prematurely; the implementation plan must "
        "address this before implementation.",
        "No Lp norm computation is permitted during the planning phase.",
    ]


def default_numerical_stability_requirements() -> list[str]:
    return [
        "For p=2 (Euclidean), the square root must be computed with a float64 "
        "square root function; no approximation is permitted.",
        "For general p, the (1/p) root must be computed with a float64 power "
        "function; the implementation plan must declare how the root is computed.",
        "For p=inf, the maximum absolute difference must be computed without "
        "any power or root operation to avoid numerical loss.",
        "Zero-difference inputs (x == y) must produce a distance of exactly 0.0 "
        "without any overflow or underflow in intermediate powers.",
        "Very large element magnitudes (near float64 max) must not overflow "
        "in the power step; a documented input-magnitude policy is required "
        "before implementation.",
    ]


def default_dependency_inventory() -> list[dict[str, Any]]:
    return [
        {
            "dependency_id": "dep_001_test_vector_pack",
            "dependency_type": "TEST_VECTOR",
            "description": (
                "Norm geometry baseline test vector from the metric operator "
                "baseline test vector pack; currently VALID_METADATA_VECTOR only; "
                "expected Lp distance fields not yet added."
            ),
            "status": "NOT_READY",
            "blocking": True,
        },
        {
            "dependency_id": "dep_002_p_parameter_convention",
            "dependency_type": "DATA_LAYOUT",
            "description": (
                "The p parameter convention (explicit float64 vs. sentinel for "
                "p=inf) must be declared before the test vector schema can be "
                "finalized."
            ),
            "status": "PLANNED_ONLY",
            "blocking": True,
        },
        {
            "dependency_id": "dep_003_vector_representation",
            "dependency_type": "DATA_LAYOUT",
            "description": (
                "The canonical vector representation format (JSON array of float64 "
                "values) must be declared before fixture schema can be defined."
            ),
            "status": "PLANNED_ONLY",
            "blocking": True,
        },
    ]


def default_implementation_prerequisites() -> list[dict[str, Any]]:
    return [
        {
            "description": (
                "MetricOperatorRank4SelectionPlan.v1 must be present selecting "
                "NORM_GEOMETRY at rank 4 with SELECTION_PLAN_ONLY scope."
            ),
            "evidence_refs": [
                "MetricOperatorRank4SelectionPlan.v1:metric_operator_rank4_selection_plan_001"
            ],
            "prereq_status": "REQUIRED",
        },
        {
            "description": (
                "MetricOperatorRank4CandidateAudit.v1 must be present confirming "
                "NORM_GEOMETRY as the rank-4 candidate."
            ),
            "evidence_refs": [
                "MetricOperatorRank4CandidateAudit.v1:metric_operator_rank4_candidate_audit_001"
            ],
            "prereq_status": "REQUIRED",
        },
        {
            "description": (
                "NormGeometryTestVectorSchemaPlan.v1 must be completed before "
                "fixture schema definitions can be created."
            ),
            "evidence_refs": [],
            "prereq_status": "DEFERRED",
        },
    ]


def default_implementation_risks() -> list[dict[str, Any]]:
    return [
        {
            "description": (
                "Float64 overflow in the power step (|x_i - y_i|^p) for large "
                "element magnitudes or large p values; must be bounded by an "
                "input-magnitude policy before implementation."
            ),
            "risk_level": "LOW",
            "mitigation": (
                "Declare maximum allowed element magnitude and p value in the "
                "implementation plan; add NOT_COMPUTABLE branch for out-of-bound inputs."
            ),
        },
        {
            "description": (
                "The p=inf sentinel convention must be fixed before "
                "implementation; ambiguous sentinel produces non-deterministic "
                "branch selection."
            ),
            "risk_level": "LOW",
            "mitigation": (
                "Declare canonical p=inf sentinel value (e.g., float('inf') or "
                "a string enum) in the data layout dependency before "
                "fixture schema is finalized."
            ),
        },
        {
            "description": (
                "For general p, underflow of individual terms near zero may "
                "silently drop small contributions; documented bound required."
            ),
            "risk_level": "LOW",
            "mitigation": (
                "Define minimum non-zero element difference threshold in the "
                "implementation plan; add a note in validation requirements."
            ),
        },
    ]


def default_validation_requirements() -> list[dict[str, Any]]:
    return [
        {
            "description": (
                "Baseline test vectors must be extended with norm-geometry-specific "
                "reference inputs (paired float64 vectors, p value) and pinned "
                "expected Lp distance scalars before implementation begins."
            ),
            "validation_type": "REFERENCE_VECTOR",
            "evidence_refs": [],
        },
        {
            "description": (
                "NOT_COMPUTABLE cases (empty vectors, mismatched lengths, p < 1, "
                "non-finite element values) must each have a dedicated validation fixture."
            ),
            "validation_type": "EDGE_CASE_VALIDATION",
            "evidence_refs": [],
        },
        {
            "description": (
                "Deterministic replay validation: identical paired vector inputs "
                "and p must produce identical Lp distance output across independent runs."
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
                "Special-case validation: p=1, p=2, and p=inf must each have "
                "dedicated reference fixtures with analytically exact expected values."
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
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_norm_geometry_distance_implementation_readiness_dossier(
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
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            "invalid_schema_version"
        )
    if packet["dossier_type"] != DOSSIER_TYPE:
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            "invalid_dossier_type"
        )
    if packet["selected_operator"] != OPERATOR_ID:
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            "unknown_selected_operator"
        )
    if packet["dossier_status"] != DOSSIER_STATUS:
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            "invalid_dossier_status"
        )
    if packet["readiness_scope"] != READINESS_SCOPE:
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            "invalid_readiness_scope"
        )
    if packet["intended_lane"] != INTENDED_LANE:
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            "invalid_intended_lane"
        )

    blocked = set(packet.get("blocked_scopes", []))
    missing_scopes = REQUIRED_BLOCKED_SCOPES - blocked
    if missing_scopes:
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            f"missing_required_blocked_scopes:{sorted(missing_scopes)}"
        )

    locks = packet["authority_locks"]
    for k in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(k) is not True:
            raise NormGeometryDistanceImplementationReadinessDossierValidationError(
                f"authority_lock_must_be_true:{k}"
            )
    for k in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(k) is not False:
            raise NormGeometryDistanceImplementationReadinessDossierValidationError(
                f"authority_lock_must_be_false:{k}"
            )

    if packet["output_contract"] != default_output_contract():
        raise NormGeometryDistanceImplementationReadinessDossierValidationError(
            "invalid_output_contract"
        )

    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise NormGeometryDistanceImplementationReadinessDossierValidationError(
                f"governance_flag_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_norm_geometry_distance_implementation_readiness_dossier_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_norm_geometry_distance_implementation_readiness_dossier(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_norm_geometry_distance_implementation_readiness_dossier(
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
        compute_norm_geometry_distance_implementation_readiness_dossier_hash(base)
    )
    validate_norm_geometry_distance_implementation_readiness_dossier(base)
    return _finalize(base)
