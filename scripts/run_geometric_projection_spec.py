"""Script: emit deterministic GeometricProjectionSpec.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.geometric_projection_spec import build_geometric_projection_spec
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P44-GEOMETRIC-PROJECTION-SPEC-001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.geometric_projection_spec_latest

_PAYLOAD: dict = {
    "item_id": "geometric_projection_spec_001",
    "title": "Geometric Projection Spec — advisory-only scaffold",
    "observed_summary": (
        "Advisory-only projection specification for the AAL-Viz geometric renderer surface. "
        "No rendering is performed. No metric values are computed. "
        "Projection-only posture. All authority flags false. "
        "Satisfies P44 source_projection_spec_refs dependency."
    ),
    "governance_flags": {
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "runtime_mutation": False,
        "forecast_influence": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "activation_approved": False,
        "authorization_granted": False,
    },
    "provenance": {
        "source": "P44_EVIDENCE_ASSEMBLY",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/geometric_projection_spec.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer_planning.v1.schema.json",
        ],
        "evidence_refs": [
            "AALVizGeometricRendererPlanning.v1:aal_viz_geometric_renderer_planning_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "geometric_projection_spec",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "geometric_projection_spec_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_geometric_projection_spec(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        __import__("json").dumps(packet, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "geometric_projection_spec_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"item_id={packet['item_id']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
