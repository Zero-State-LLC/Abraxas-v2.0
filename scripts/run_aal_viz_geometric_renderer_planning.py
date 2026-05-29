"""Script: emit deterministic AAL-Viz geometric renderer planning artifact."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.aal_viz_geometric_renderer_planning import (
    build_aal_viz_geometric_renderer_planning,
    default_implementation_gates,
    default_output_contract,
    default_renderer_constraints,
    serialize_aal_viz_geometric_renderer_planning,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P43-AAL-VIZ-GEOMETRIC-RENDERER-PLANNING-001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.aal_viz_geometric_renderer_planning_latest

_PAYLOAD: dict = {
    "planning_id": "aal_viz_geometric_renderer_planning_001",
    "renderer_scope": {
        "target_surface_family": "MULTI_SURFACE_PLANNING",
        "intended_lane": "PROJECTION",
        "planning_stage": "RENDERER_NOT_IMPLEMENTED",
        "scope_note": (
            "Planning-only gate for future AAL-Viz geometric renderer tracks. "
            "No renderer implementation is present. "
            "All surface families remain in RENDERER_NOT_IMPLEMENTED state."
        ),
    },
    "planned_surfaces": [
        {
            "surface_id": "surface-001-multi-surface-plan",
            "surface_family": "MULTI_SURFACE_PLANNING",
            "description": (
                "Aggregate planning surface for future geometric projection tracks. "
                "No active visual output is produced at this stage."
            ),
            "source_placeholder_refs": [
                "GeometricProjectionSpec.v1:projection-spec-001",
            ],
            "visual_requirements": [
                "deterministic_layer_ordering",
                "projection_only_advisory_posture",
            ],
            "implementation_status": "RENDERER_NOT_IMPLEMENTED",
            "evidence_required": "PROJECTION_SPEC_REF_REQUIRED",
        },
        {
            "surface_id": "surface-002-manifold-transport-plan",
            "surface_family": "MANIFOLD_TRANSPORT",
            "description": (
                "Planning surface for manifold transport geometry. "
                "Blocked pending projection spec and test vector review."
            ),
            "source_placeholder_refs": [
                "GeometricProjectionSpec.v1:manifold-transport-spec-001",
            ],
            "visual_requirements": [
                "deterministic_layer_ordering",
                "projection_only_advisory_posture",
                "no_runtime_effect",
            ],
            "implementation_status": "BLOCKED_PENDING_OPERATOR_REVIEW",
            "evidence_required": "PROJECTION_SPEC_REF_REQUIRED",
        },
        {
            "surface_id": "surface-003-trust-geometry-plan",
            "surface_family": "TRUST_GEOMETRY",
            "description": (
                "Planning surface for trust geometry overlay. "
                "Requires metric registry ref before implementation planning."
            ),
            "source_placeholder_refs": [
                "MetricRegistry.v1:trust-geometry-ref-001",
            ],
            "visual_requirements": [
                "deterministic_layer_ordering",
                "projection_only_advisory_posture",
                "no_runtime_effect",
            ],
            "implementation_status": "BLOCKED_PENDING_OPERATOR_REVIEW",
            "evidence_required": "METRIC_REGISTRY_REF_REQUIRED",
        },
    ],
    "source_projection_spec_refs": [
        "GeometricProjectionSpec.v1:projection-spec-001",
    ],
    "source_metric_registry_refs": [],
    "source_test_vector_pack_refs": [],
    "source_oracle_replay_receipt_refs": [],
    "source_yggdrasil_replay_receipt_refs": [],
    "renderer_constraints": default_renderer_constraints(),
    "implementation_gates": default_implementation_gates(),
    "output_contract": default_output_contract(),
    "governance_flags": {
        "advisory_only": True,
        "planning_only": True,
        "non_authoritative": True,
        "deterministic": True,
        "read_only": True,
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
        "advisory_only": True,
        "deterministic": True,
        "planning_only": True,
        "non_authoritative": True,
        "read_only": True,
        "source_linked": True,
        "patch_id": PATCH_ID,
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def _build_markdown(packet: dict) -> str:
    surfaces = packet.get("planned_surfaces", [])
    lines = [
        "# P43 AAL-Viz Geometric Renderer Planning",
        "",
        f"- planning_id: `{packet.get('planning_id', '?')}`",
        f"- planning_type: `{packet.get('planning_type', '?')}`",
        f"- schema_version: `{packet.get('schema_version', '?')}`",
        f"- canonical_hash: `{packet.get('canonical_hash', '?')}`",
        f"- created_at_utc: `{packet.get('created_at_utc', '?')}`",
        "",
        "## Renderer Scope",
        f"- target_surface_family: `{packet.get('renderer_scope', {}).get('target_surface_family', '?')}`",
        f"- intended_lane: `{packet.get('renderer_scope', {}).get('intended_lane', '?')}`",
        f"- planning_stage: `{packet.get('renderer_scope', {}).get('planning_stage', '?')}`",
        "",
        f"## Planned Surfaces ({len(surfaces)})",
    ]
    for s in surfaces:
        lines += [
            f"### {s.get('surface_id', '?')}",
            f"- family: `{s.get('surface_family', '?')}`",
            f"- status: `{s.get('implementation_status', '?')}`",
            f"- evidence_required: `{s.get('evidence_required', '?')}`",
            f"- description: {s.get('description', '')}",
            "",
        ]
    lines += [
        "## Implementation Gates",
        *(f"- {k}: `{v}`" for k, v in sorted(packet.get("implementation_gates", {}).items())),
        "",
        "## Governance",
        "- advisory_only: `true`",
        "- planning_only: `true`",
        "- renderer_implemented: `false`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "aal_viz_geometric_renderer_planning",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(logger, "INFO", "aal_viz_geometric_renderer_planning_started",
              artifact_path=OUT_PATH.as_posix(), correlation_id=correlation_id)

    packet = build_aal_viz_geometric_renderer_planning(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(serialize_aal_viz_geometric_renderer_planning(packet), encoding="utf-8")
    OUT_PATH.with_suffix(".md").write_text(_build_markdown(packet), encoding="utf-8")

    log_event(logger, "INFO", "aal_viz_geometric_renderer_planning_completed",
              artifact_path=OUT_PATH.as_posix(),
              canonical_hash=packet.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"planning_id={packet['planning_id']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
