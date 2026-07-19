"""Runner: emit AAL-Viz Geometric Renderer WebGL Boundary artifact."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from core.aal_viz_geometric_renderer_webgl import (
    build_aal_viz_geometric_renderer_webgl,
    default_authority_locks,
    default_blocked_scopes,
    default_governance_flags,
    default_renderer_output_declaration,
    default_validation_rules,
    default_webgl_intake_record,
    serialize_aal_viz_geometric_renderer_webgl,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

OUT_DIR = Path("out/projections")
OUT_PATH = OUT_DIR / "aal_viz_geometric_renderer_webgl_001.latest.json"

_VIEWMODEL_REF = {
    "schema_version": "GeometricProjectionSpec.v1",
    "title": "Geometric Projection Spec \u2014 advisory-only scaffold",
    "source_hash": "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080",
    "observed_summary": "Advisory-only projection.",
    "governance_flags": {},
    "provenance": {},
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> None:
    payload = {
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_006",
        "viewmodel_ref": _VIEWMODEL_REF,
        "webgl_intake_record": default_webgl_intake_record(_VIEWMODEL_REF),
        "renderer_output_declaration": default_renderer_output_declaration(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of RENDERER_WEBGL_BOUNDARY_DEFINED status, the three-surface "
            "renderer boundary chain (SVG, Canvas, WebGL) is complete. Advance to cross-surface "
            "parity hardening audit or operator decision for metric computation authorization. "
            "All other blocked scopes remain unchanged."
        ),
        "provenance": {
            "source": "P44_WEBGL_RENDERER_BOUNDARY_GATE",
            "advisory_only": True,
            "generated_by": "PATCH-P44-RENDERER-WEBGL-BOUNDARY-001",
            "evidence_refs": [
                "AALVizGeometricRendererCanvas.v1:aal_viz_geometric_renderer_canvas_001",
                "GeometricProjectionSpec.v1:geometric_projection_spec_001",
                "P44OperatorWebGLDecision.v1:P44_OPERATOR_DECISION_2026_05_29_006",
            ],
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer_webgl.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_canvas.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet = build_aal_viz_geometric_renderer_webgl(payload)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_aal_viz_geometric_renderer_webgl(packet), encoding="utf-8"
    )

    log.info(json.dumps({
        "event": "webgl_renderer_boundary_emitted",
        "artifact_path": str(OUT_PATH),
        "renderer_webgl_status": packet["renderer_webgl_status"],
        "canonical_hash": packet["canonical_hash"],
        "source_canvas_renderer_boundary_hash": packet["source_canvas_renderer_boundary_hash"],
        "emits_webgl": packet["renderer_output_declaration"]["emits_webgl"],
        "webgl_renderer_implementation_authorized": (
            packet["authority_locks"]["webgl_renderer_implementation_authorized"]
        ),
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.error("webgl_renderer_boundary_runner_failed: %s", exc)
        sys.exit(1)
