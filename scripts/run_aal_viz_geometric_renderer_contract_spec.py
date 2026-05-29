"""Script: emit deterministic AAL-Viz Geometric Renderer Contract Specification artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.aal_viz_geometric_renderer_contract_spec import (
    build_aal_viz_geometric_renderer_contract_spec,
    default_authority_locks,
    default_blocked_scopes,
    default_deterministic_ordering_contract,
    default_governance_flags,
    default_renderer_input_contract,
    default_renderer_output_contract,
    default_source_ref_preservation_rules,
    default_validation_rules,
    default_viewmodel_acceptance_rules,
    serialize_aal_viz_geometric_renderer_contract_spec,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P44-RENDERER-CONTRACT-SPEC-001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.aal_viz_geometric_renderer_contract_spec_latest

_PAYLOAD: dict = {
    "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_002",
    "renderer_input_contract": default_renderer_input_contract(),
    "renderer_output_contract": default_renderer_output_contract(),
    "viewmodel_acceptance_rules": default_viewmodel_acceptance_rules(),
    "deterministic_ordering_contract": default_deterministic_ordering_contract(),
    "source_ref_preservation_rules": default_source_ref_preservation_rules(),
    "validation_rules": default_validation_rules(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "governance_flags": default_governance_flags(),
    "recommended_next_step": (
        "After operator review of RENDERER_CONTRACT_SPEC_DEFINED status, "
        "advance to operator decision for renderer implementation authorization. "
        "Renderer code, metric computation, and P43 surface lanes remain blocked "
        "until a separate operator decision explicitly authorizes renderer implementation."
    ),
    "provenance": {
        "source": "P44_RENDERER_CONTRACT_SPEC_GATE",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "evidence_refs": [
            "AALVizGeometricRendererViewmodelAdapterSpec.v1:aal_viz_geometric_renderer_viewmodel_adapter_spec_001",
            "AALVizGeometricRendererWP001ImplementationBoundary.v1:wp001_implementation_boundary_001",
            "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
            "GeometricProjectionSpec.v1:geometric_projection_spec_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "OracleGeometricAttachmentReplayReceipt.v1:oracle_geometric_attachment_replay_receipt_001",
            "YggdrasilGeometricRouteReplayReceipt.v1:yggdrasil_geometric_route_replay_receipt_001",
            "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_002",
        ],
        "upstream_schema_refs": [
            "contracts/canon/aal_viz_geometric_renderer_contract_spec.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer_viewmodel_adapter_spec.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer_wp001_implementation_boundary.v1.schema.json",
            "contracts/canon/geometric_projection_spec.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "aal_viz_geometric_renderer_contract_spec",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_contract_spec_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_aal_viz_geometric_renderer_contract_spec(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_aal_viz_geometric_renderer_contract_spec(packet),
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_contract_spec_completed",
        artifact_path=OUT_PATH.as_posix(),
        contract_spec_status=packet.get("contract_spec_status", "?"),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"contract_spec_id={packet['contract_spec_id']}")
    print(f"contract_spec_status={packet.get('contract_spec_status', '?')}")
    print(f"source_viewmodel_adapter_spec_hash={packet.get('source_viewmodel_adapter_spec_hash', '?')}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
