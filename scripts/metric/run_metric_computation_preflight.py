"""Runner: emit Metric Computation Preflight boundary artifact."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from core.metric_computation_preflight import (
    build_metric_computation_preflight,
    default_authority_locks,
    default_blocked_scopes,
    default_governance_flags,
    default_metric_intake_record,
    default_preflight_governance_acknowledgements,
    default_renderer_output_declaration,
    default_validation_rules,
    serialize_metric_computation_preflight,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

OUT_DIR = Path("out/projections")
OUT_PATH = OUT_DIR / "metric_computation_preflight_001.latest.json"

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
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_007",
        "viewmodel_ref": _VIEWMODEL_REF,
        "metric_intake_record": default_metric_intake_record(_VIEWMODEL_REF),
        "renderer_output_declaration": default_renderer_output_declaration(),
        "preflight_governance_acknowledgements": default_preflight_governance_acknowledgements(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of METRIC_COMPUTATION_PREFLIGHT_DEFINED status, "
            "advance to metric operator implementation selection — select the first operator "
            "(WASSERSTEIN, rank 1) for shadow-lane preflight implementation planning. "
            "All other blocked scopes remain unchanged. "
            "Forecast authority, inference authority, and P43 surface lanes remain blocked."
        ),
        "provenance": {
            "source": "P44_METRIC_COMPUTATION_PREFLIGHT_GATE",
            "advisory_only": True,
            "generated_by": "PATCH_P44_METRIC_COMPUTATION_PREFLIGHT_001",
            "evidence_refs": [
                "AALVizGeometricRendererWebGL.v1:aal_viz_geometric_renderer_webgl_001",
                "MetricOperatorRegistry.v1:metric_operator_registry_001",
                "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
                "P44OperatorMetricPreflightDecision.v1:P44_OPERATOR_DECISION_2026_05_29_007",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_computation_preflight.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_webgl.v1.schema.json",
                "contracts/canon/metric_operator_registry.v1.schema.json",
                "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet = build_metric_computation_preflight(payload)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_metric_computation_preflight(packet), encoding="utf-8"
    )

    log.info(json.dumps({
        "event": "metric_computation_preflight_emitted",
        "artifact_path": str(OUT_PATH),
        "preflight_status": packet["preflight_status"],
        "canonical_hash": packet["canonical_hash"],
        "source_webgl_renderer_boundary_hash": packet["source_webgl_renderer_boundary_hash"],
        "source_metric_registry_hash": packet["source_metric_registry_hash"],
        "source_baseline_vector_pack_hash": packet["source_baseline_vector_pack_hash"],
        "metric_computation_authorized": (
            packet["authority_locks"]["metric_computation_authorized"]
        ),
        "emits_metric_values": packet["renderer_output_declaration"]["emits_metric_values"],
        "forecast_influence": packet["renderer_output_declaration"]["forecast_influence"],
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.error("metric_computation_preflight_runner_failed: %s", exc)
        sys.exit(1)
