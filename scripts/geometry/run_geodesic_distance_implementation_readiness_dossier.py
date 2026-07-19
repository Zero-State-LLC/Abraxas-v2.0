"""Script: emit deterministic GeodesicDistanceImplementationReadinessDossier.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.geodesic_distance_implementation_readiness_dossier import (
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    build_geodesic_distance_implementation_readiness_dossier,
    default_authority_locks,
    default_blocked_scopes,
    default_dependency_inventory,
    default_determinism_requirements,
    default_implementation_prerequisites,
    default_implementation_risks,
    default_input_shape_requirements,
    default_mathematical_requirements,
    default_numerical_constraints,
    default_numerical_stability_requirements,
    default_output_contract,
    default_validation_requirements,
    serialize_geodesic_distance_implementation_readiness_dossier,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_GEODESIC_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.geodesic_distance_implementation_readiness_dossier_latest

_PAYLOAD: dict = {
    "dossier_id": "geodesic_distance_implementation_readiness_dossier_001",
    "implementation_scope": {
        "mode": "PLANNING_ONLY",
        "planning_lane": "SHADOW_METRIC_OPERATOR",
        "readiness_status": "GEODESIC_READINESS_DOSSIER_DEFINED",
    },
    "mathematical_requirements": default_mathematical_requirements(),
    "input_shape_requirements": default_input_shape_requirements(),
    "determinism_requirements": default_determinism_requirements(),
    "numerical_constraints": default_numerical_constraints(),
    "numerical_stability_requirements": default_numerical_stability_requirements(),
    "dependency_inventory": default_dependency_inventory(),
    "implementation_prerequisites": default_implementation_prerequisites(),
    "implementation_risks": default_implementation_risks(),
    "validation_requirements": default_validation_requirements(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_GOVERNANCE_FLAGS},
    "provenance": {
        "source": "GEODESIC_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER_001",
        "evidence_refs": [
            "MetricOperatorRank3SelectionPlan.v1:"
            "metric_operator_rank3_selection_plan_001",
            "MetricOperatorRank3CandidateAudit.v1:"
            "metric_operator_rank3_candidate_audit_001",
            "MetricOperatorRegistryStabilization.v1:"
            "metric_operator_registry_stabilization_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "geodesic_distance_implementation_readiness_dossier.v1.schema.json",
            "contracts/canon/"
            "metric_operator_rank3_selection_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "geodesic_distance_implementation_readiness_dossier",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "geodesic_distance_implementation_readiness_dossier_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_geodesic_distance_implementation_readiness_dossier(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_geodesic_distance_implementation_readiness_dossier(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "geodesic_distance_implementation_readiness_dossier_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"dossier_id={packet['dossier_id']}")
    print(f"dossier_type={packet['dossier_type']}")
    print(f"dossier_status={packet['dossier_status']}")
    print(f"selected_operator={packet['selected_operator']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
