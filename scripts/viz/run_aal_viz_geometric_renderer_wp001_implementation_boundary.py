"""Script: emit deterministic AAL-Viz Geometric Renderer WP-001 Implementation Boundary artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.aal_viz_geometric_renderer_wp001_implementation_boundary import (
    build_aal_viz_geometric_renderer_wp001_implementation_boundary,
    default_adapter_interface_plan,
    default_authority_locks,
    default_blocked_scopes,
    default_deterministic_ordering_contract,
    default_governance_flags,
    default_source_reference_matrix,
    serialize_aal_viz_geometric_renderer_wp001_implementation_boundary,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P44-WP001-IMPLEMENTATION-BOUNDARY-001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.aal_viz_geometric_renderer_wp001_implementation_boundary_latest

_PAYLOAD: dict = {
    "source_p44_plan_hash": "e747808d3a94586fd682ece6a0824b666ac0aa326c0368799d736d85c11864f1",
    "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_002",
    "adapter_interface_plan": default_adapter_interface_plan(),
    "deterministic_ordering_contract": default_deterministic_ordering_contract(),
    "source_reference_matrix": default_source_reference_matrix(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "governance_flags": default_governance_flags(),
    "recommended_next_step": (
        "After operator review of WP001_IMPLEMENTATION_BOUNDARY_DEFINED status, "
        "author the viewmodel adapter specification document for wp-001-implementation-boundary. "
        "Renderer code, metric computation, and P43 surface lanes remain blocked."
    ),
    "provenance": {
        "source": "P44_WP001_IMPLEMENTATION_BOUNDARY_GATE",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "evidence_refs": [
            "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
            "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_002",
            "GeometricProjectionSpec.v1:geometric_projection_spec_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "OracleGeometricAttachmentReplayReceipt.v1:oracle_geometric_attachment_replay_receipt_001",
            "YggdrasilGeometricRouteReplayReceipt.v1:yggdrasil_geometric_route_replay_receipt_001",
        ],
        "upstream_schema_refs": [
            "contracts/canon/aal_viz_geometric_renderer_wp001_implementation_boundary.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer_implementation_plan.v1.schema.json",
            "contracts/canon/geometric_projection_spec.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "aal_viz_geometric_renderer_wp001_implementation_boundary",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_wp001_implementation_boundary_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_aal_viz_geometric_renderer_wp001_implementation_boundary(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_aal_viz_geometric_renderer_wp001_implementation_boundary(packet),
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_wp001_implementation_boundary_completed",
        artifact_path=OUT_PATH.as_posix(),
        wp_status=packet.get("wp_status", "?"),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"work_package_id={packet['work_package_id']}")
    print(f"wp_status={packet.get('wp_status', '?')}")
    print(f"implementation_stage={packet.get('implementation_stage', '?')}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
