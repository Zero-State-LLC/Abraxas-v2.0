"""Script: emit deterministic AAL-Viz Geometric Renderer Boundary artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.aal_viz_geometric_renderer import (
    build_aal_viz_geometric_renderer,
    default_authority_locks,
    default_blocked_scopes,
    default_deterministic_ordering_result,
    default_governance_flags,
    default_renderer_intake_boundary,
    default_renderer_output_declaration,
    default_validation_rules,
    default_viewmodel_acceptance_result,
    serialize_aal_viz_geometric_renderer,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P44-RENDERER-BOUNDARY-001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.aal_viz_geometric_renderer_latest

_PAYLOAD: dict = {
    "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_003",
    "renderer_intake_boundary": default_renderer_intake_boundary(),
    "viewmodel_acceptance_result": default_viewmodel_acceptance_result(),
    "deterministic_ordering_result": default_deterministic_ordering_result(),
    "renderer_output_declaration": default_renderer_output_declaration(),
    "validation_rules": default_validation_rules(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "governance_flags": default_governance_flags(),
    "recommended_next_step": (
        "After operator review of RENDERER_BOUNDARY_DEFINED status, advance to "
        "operator decision for SVG/WebGL/Canvas renderer surface authorization. "
        "All renderer technology surfaces remain blocked. Metric computation remains "
        "blocked. P43 surface lanes remain blocked."
    ),
    "provenance": {
        "source": "P44_RENDERER_BOUNDARY_GATE",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "evidence_refs": [
            "AALVizGeometricRendererContractSpec.v1:aal_viz_geometric_renderer_contract_spec_001",
            "AALVizGeometricRendererViewmodelAdapterSpec.v1:aal_viz_geometric_renderer_viewmodel_adapter_spec_001",
            "AALVizGeometricRendererWP001ImplementationBoundary.v1:wp001_implementation_boundary_001",
            "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
            "GeometricProjectionSpec.v1:geometric_projection_spec_001",
            "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_003",
        ],
        "upstream_schema_refs": [
            "contracts/canon/aal_viz_geometric_renderer.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer_contract_spec.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer_viewmodel_adapter_spec.v1.schema.json",
            "contracts/canon/geometric_projection_spec.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "aal_viz_geometric_renderer",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_aal_viz_geometric_renderer(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_aal_viz_geometric_renderer(packet),
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_completed",
        artifact_path=OUT_PATH.as_posix(),
        renderer_status=packet.get("renderer_status", "?"),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"renderer_id={packet['renderer_id']}")
    print(f"renderer_status={packet.get('renderer_status', '?')}")
    print(f"source_renderer_contract_spec_hash={packet.get('source_renderer_contract_spec_hash', '?')}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
