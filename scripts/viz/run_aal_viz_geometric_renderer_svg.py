"""Script: emit deterministic AAL-Viz Geometric Renderer SVG Boundary artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.aal_viz_geometric_renderer_svg import (
    build_aal_viz_geometric_renderer_svg,
    default_authority_locks,
    default_blocked_scopes,
    default_governance_flags,
    default_renderer_output_declaration,
    default_validation_rules,
    serialize_aal_viz_geometric_renderer_svg,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P44-RENDERER-SVG-BOUNDARY-001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.aal_viz_geometric_renderer_svg_latest

# Construct viewmodel_ref from the GeometricProjectionSpec artifact
# by applying the PASSTHROUGH_DECLARED_ONLY field mapping defined in the adapter spec.
_GEO_SPEC_PATH = Path(
    "out/projections/geometric_projection_spec_001.latest.json"
)
if _GEO_SPEC_PATH.exists():
    _geo = json.loads(_GEO_SPEC_PATH.read_text(encoding="utf-8"))
    _VIEWMODEL_REF = {
        "created_at_utc": _geo.get("created_at_utc", ""),
        "governance_flags": _geo.get("governance_flags", {}),
        "observed_summary": _geo.get("observed_summary", ""),
        "provenance": _geo.get("provenance", {}),
        "schema_version": _geo.get("schema_version", ""),
        "source_hash": _geo.get("canonical_hash", ""),
        "title": _geo.get("title", ""),
    }
else:
    _VIEWMODEL_REF = {
        "schema_version": "GeometricProjectionSpec.v1",
        "title": "Geometric Projection Spec \u2014 advisory-only scaffold",
        "source_hash": "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080",
        "observed_summary": (
            "Advisory-only projection specification for the AAL-Viz geometric renderer surface."
        ),
        "governance_flags": {},
        "provenance": {},
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

_PAYLOAD: dict = {
    "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_004",
    "viewmodel_ref": _VIEWMODEL_REF,
    "svg_intake_record": {
        "execution_authority": False,
        "input_fields_accepted": sorted(
            ["adapter_status", "projection_boundary_id", "viewmodel_ref"]
        ),
        "ordering_applied": "CANONICAL_JSON_SORT",
        "projection_only": True,
        "svg_generation_status": "BOUNDARY_PROJECTION_ONLY",
        "viewmodel_schema_version": _VIEWMODEL_REF.get("schema_version", ""),
    },
    "renderer_output_declaration": default_renderer_output_declaration(),
    "validation_rules": default_validation_rules(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "governance_flags": default_governance_flags(),
    "recommended_next_step": (
        "After operator review of RENDERER_SVG_BOUNDARY_DEFINED status, advance to "
        "operator decision for Canvas or WebGL renderer surface authorization, or for "
        "metric computation authorization. All remaining renderer technology surfaces "
        "remain blocked. P43 surface lanes remain blocked."
    ),
    "provenance": {
        "source": "P44_SVG_RENDERER_BOUNDARY_GATE",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "evidence_refs": [
            "AALVizGeometricRenderer.v1:aal_viz_geometric_renderer_001",
            "AALVizGeometricRendererContractSpec.v1:aal_viz_geometric_renderer_contract_spec_001",
            "AALVizGeometricRendererViewmodelAdapterSpec.v1:aal_viz_geometric_renderer_viewmodel_adapter_spec_001",
            "GeometricProjectionSpec.v1:geometric_projection_spec_001",
            "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_004",
        ],
        "upstream_schema_refs": [
            "contracts/canon/aal_viz_geometric_renderer_svg.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer_contract_spec.v1.schema.json",
            "contracts/canon/geometric_projection_spec.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "aal_viz_geometric_renderer_svg",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_svg_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_aal_viz_geometric_renderer_svg(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_aal_viz_geometric_renderer_svg(packet),
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_svg_completed",
        artifact_path=OUT_PATH.as_posix(),
        renderer_svg_status=packet.get("renderer_svg_status", "?"),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"renderer_svg_id={packet['renderer_svg_id']}")
    print(f"renderer_svg_status={packet.get('renderer_svg_status', '?')}")
    print(f"source_renderer_boundary_hash={packet.get('source_renderer_boundary_hash', '?')}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
