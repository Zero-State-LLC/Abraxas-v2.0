from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicDistanceImplementationReadinessDossier.v1"
DOSSIER_TYPE = "GEODESIC_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER"
OPERATOR_ID = "GEODESIC"
INTENDED_LANE = "SHADOW"
READINESS_SCOPE = "IMPLEMENTATION_READINESS_ONLY"
DOSSIER_STATUS = "GEODESIC_READINESS_DOSSIER_DEFINED"

REQUIRED_BLOCKED_SCOPES: frozenset[str] = frozenset({
    "geodesic_computation",
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
    "geodesic_computation_authorized",
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
    "dijkstra-execution", "numpy", "scipy", "gpu-kernel",
)


class GeodesicDistanceImplementationReadinessDossierValidationError(ValueError):
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
        "Geodesic distance on a finite weighted graph is defined as the length of the shortest path between source and target nodes under a given edge-weight metric.",
        "For graphs with non-negative edge weights: Dijkstra's algorithm computes exact shortest paths in O((V + E) log V) time; fully deterministic with stable tie-breaking on node IDs.",
        "For unweighted graphs (all edge weights equal to 1.0): BFS computes exact shortest paths in O(V + E) time; fully deterministic with sorted adjacency traversal order.",
        "Self-loop case (source_node == target_node): geodesic distance is defined as 0.0 by convention; no path traversal required.",
        "All-pairs geodesic (Floyd-Warshall, O(V^3)): declared as a future extension; not included in the baseline plan scope.",
        "Negative edge weights are not supported in the baseline plan; such inputs must route to NOT_COMPUTABLE without invoking any distance algorithm.",
    ]


def default_input_shape_requirements() -> list[str]:
    return [
        "Graph must be represented as a finite set of nodes and a finite set of directed or undirected edges, each with a non-negative float64 weight.",
        "source_node and target_node must be declared as node identifiers present in the graph.",
        "Edge weights must be float64; non-negative; negative weights produce a NOT_COMPUTABLE result.",
        "Empty graph (zero nodes or zero edges with source != target) produces a NOT_COMPUTABLE result.",
        "Disconnected graph (no path from source_node to target_node) produces a NOT_COMPUTABLE result.",
        "Source_node or target_node not present in the graph node set produces a NOT_COMPUTABLE result.",
        "Self-loop edges (same source and target node) are permitted and must not cause infinite traversal.",
    ]


def default_determinism_requirements() -> list[str]:
    return [
        "Dijkstra's algorithm with a deterministic priority-queue tie-breaking rule (e.g., lexicographic ordering on node IDs) is fully deterministic given identical inputs.",
        "BFS for unweighted graphs is fully deterministic given a sorted adjacency list traversal order.",
        "All geodesic computations must produce identical results across independent runs given identical graph inputs and algorithm parameters.",
        "Node ID ordering must be stable and documented before implementation.",
        "No randomized or probabilistic algorithm components are permitted in the baseline plan.",
    ]


def default_numerical_constraints() -> list[str]:
    return [
        "Float64 precision required for all edge weights and path-length accumulation.",
        "Float32 is excluded from the baseline plan.",
        "Hash and serialization determinism required across all dossier fields.",
        "No floating-point geodesic kernel execution is permitted during the planning phase.",
        "Path-length accumulation error over long paths (many edges) must be bounded and documented before implementation.",
    ]


def default_numerical_stability_requirements() -> list[str]:
    return [
        "Zero-weight edges are valid and must not cause infinite loops or division-by-zero in path accumulation.",
        "Very long paths (large number of edges) may accumulate float64 rounding error; acceptable bound must be declared before implementation.",
        "Disconnected graphs must be detected and produce NOT_COMPUTABLE without infinite traversal.",
        "Graphs with all equal edge weights must produce deterministic results identical to BFS.",
        "Degenerate inputs (single node, source == target) must produce distance 0.0 without algorithm invocation.",
    ]


def default_dependency_inventory() -> list[dict[str, Any]]:
    return [
        {
            "dependency_id": "dep_001_test_vector_pack",
            "dependency_type": "TEST_VECTOR",
            "description": "Geodesic baseline test vector from the metric operator baseline test vector pack; currently VALID_METADATA_VECTOR only; expected_geodesic_distance fields not yet added.",
            "status": "NOT_READY",
            "blocking": True,
        },
        {
            "dependency_id": "dep_002_graph_data_layout",
            "dependency_type": "DATA_LAYOUT",
            "description": "Adjacency-list or adjacency-matrix graph representation must be declared before fixture schema can be defined.",
            "status": "PLANNED_ONLY",
            "blocking": True,
        },
        {
            "dependency_id": "dep_003_node_id_ordering",
            "dependency_type": "DATA_LAYOUT",
            "description": "Canonical node ID ordering (lexicographic or integer) must be declared to guarantee deterministic traversal.",
            "status": "PLANNED_ONLY",
            "blocking": True,
        },
    ]


def default_implementation_prerequisites() -> list[dict[str, Any]]:
    return [
        {
            "description": "MetricOperatorRank3SelectionPlan.v1 must be present selecting GEODESIC at rank 3 with SELECTION_PLAN_ONLY scope.",
            "evidence_refs": ["MetricOperatorRank3SelectionPlan.v1:metric_operator_rank3_selection_plan_001"],
            "prereq_status": "REQUIRED",
        },
        {
            "description": "MetricOperatorRank3CandidateAudit.v1 must be present confirming GEODESIC as the rank-3 candidate.",
            "evidence_refs": ["MetricOperatorRank3CandidateAudit.v1:metric_operator_rank3_candidate_audit_001"],
            "prereq_status": "REQUIRED",
        },
        {
            "description": "GeodesicTestVectorSchemaPlan.v1 must be completed before fixture schema files can be defined.",
            "evidence_refs": [],
            "prereq_status": "DEFERRED",
        },
    ]


def default_implementation_risks() -> list[dict[str, Any]]:
    return [
        {
            "description": "Graph connectivity is not guaranteed; disconnected-graph detection must be explicitly planned before implementation to avoid non-termination.",
            "risk_level": "MEDIUM",
            "mitigation": "Require NOT_COMPUTABLE branch in algorithm plan for disconnected source-to-target path.",
        },
        {
            "description": "Node ID ordering policy must be fixed before implementation; ambiguous ordering produces non-deterministic results in Dijkstra tie-breaking.",
            "risk_level": "MEDIUM",
            "mitigation": "Declare canonical node ID ordering in graph data layout before fixture schema is finalized.",
        },
        {
            "description": "Very large graphs may exceed acceptable O((V+E) log V) time bounds; size policy must be declared before implementation.",
            "risk_level": "LOW",
            "mitigation": "Define maximum graph size policy (V, E bounds) in the implementation plan.",
        },
    ]


def default_validation_requirements() -> list[dict[str, Any]]:
    return [
        {
            "description": "Baseline test vectors must be extended with geodesic-specific reference inputs and pinned expected output scalars (expected_geodesic_distance fields) before implementation begins.",
            "validation_type": "REFERENCE_VECTOR",
            "evidence_refs": [],
        },
        {
            "description": "NOT_COMPUTABLE cases (empty graph, disconnected graph, missing source/target node, negative edge weight) must each have a dedicated validation fixture.",
            "validation_type": "EDGE_CASE_VALIDATION",
            "evidence_refs": [],
        },
        {
            "description": "Deterministic replay validation: identical graph inputs must produce identical distance output across independent runs.",
            "validation_type": "DETERMINISTIC_REPLAY",
            "evidence_refs": [],
        },
        {
            "description": "Float64 precision validation: path-length accumulation must use float64 throughout; no float32 intermediate values permitted.",
            "validation_type": "NUMERICAL_STABILITY",
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
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_geodesic_distance_implementation_readiness_dossier(
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
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            "invalid_schema_version"
        )
    if packet["dossier_type"] != DOSSIER_TYPE:
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            "invalid_dossier_type"
        )
    if packet["selected_operator"] != OPERATOR_ID:
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            "unknown_selected_operator"
        )
    if packet["dossier_status"] != DOSSIER_STATUS:
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            "invalid_dossier_status"
        )
    if packet["readiness_scope"] != READINESS_SCOPE:
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            "invalid_readiness_scope"
        )
    if packet["intended_lane"] != INTENDED_LANE:
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            "invalid_intended_lane"
        )

    blocked = set(packet.get("blocked_scopes", []))
    missing_scopes = REQUIRED_BLOCKED_SCOPES - blocked
    if missing_scopes:
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            f"missing_required_blocked_scopes:{sorted(missing_scopes)}"
        )

    locks = packet["authority_locks"]
    for k in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(k) is not True:
            raise GeodesicDistanceImplementationReadinessDossierValidationError(
                f"authority_lock_must_be_true:{k}"
            )
    for k in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(k) is not False:
            raise GeodesicDistanceImplementationReadinessDossierValidationError(
                f"authority_lock_must_be_false:{k}"
            )

    if packet["output_contract"] != default_output_contract():
        raise GeodesicDistanceImplementationReadinessDossierValidationError(
            "invalid_output_contract"
        )

    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise GeodesicDistanceImplementationReadinessDossierValidationError(
                f"governance_flag_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_geodesic_distance_implementation_readiness_dossier_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_geodesic_distance_implementation_readiness_dossier(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_geodesic_distance_implementation_readiness_dossier(
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
    base["canonical_hash"] = compute_geodesic_distance_implementation_readiness_dossier_hash(
        base
    )
    validate_geodesic_distance_implementation_readiness_dossier(base)
    return _finalize(base)
