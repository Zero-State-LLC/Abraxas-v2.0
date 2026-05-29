"""Script: emit deterministic AAL-Viz geometric renderer implementation plan artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.aal_viz_geometric_renderer_implementation_plan import (
    build_aal_viz_geometric_renderer_implementation_plan,
    default_dependency_map,
    default_implementation_constraints,
    default_output_contract,
    default_renderer_work_packages,
    default_validation_plan,
    serialize_aal_viz_geometric_renderer_implementation_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P44-AAL-VIZ-GEOMETRIC-RENDERER-IMPLEMENTATION-PLAN-003-WORK-PACKAGE-DEFINITION"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.aal_viz_geometric_renderer_implementation_plan_latest

_PAYLOAD: dict = {
    "plan_id": "aal_viz_geometric_renderer_implementation_plan_001",
    "implementation_scope": {
        "target_renderer_family": "MULTI_SURFACE_RENDERER_PLANNING",
        "intended_lane": "PROJECTION",
        "implementation_stage": "WORK_PACKAGE_DEFINITION_ONLY",
    },
    "source_renderer_planning_refs": [
        "AALVizGeometricRendererPlanning.v1:aal_viz_geometric_renderer_planning_001",
    ],
    "source_projection_spec_refs": [
        "GeometricProjectionSpec.v1:geometric_projection_spec_001",
    ],
    "source_metric_registry_refs": [
        "MetricOperatorRegistry.v1:metric_operator_registry_001",
    ],
    "source_test_vector_pack_refs": [
        "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
    ],
    "renderer_work_packages": default_renderer_work_packages(),
    "dependency_map": default_dependency_map(),
    "implementation_constraints": default_implementation_constraints(),
    "validation_plan": default_validation_plan(),
    "output_contract": default_output_contract(),
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
        "source": "P44_AAL_VIZ_GEOMETRIC_RENDERER_IMPLEMENTATION_PLAN_GATE",
        "evidence_refs": [
            "AALVizGeometricRendererPlanning.v1:aal_viz_geometric_renderer_planning_001",
            "GeometricProjectionSpec.v1:geometric_projection_spec_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "OracleGeometricAttachmentReplayReceipt.v1:oracle_geometric_attachment_replay_receipt_001",
            "YggdrasilGeometricRouteReplayReceipt.v1:yggdrasil_geometric_route_replay_receipt_001",
            "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_001",
            "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_002",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/aal_viz_geometric_renderer_implementation_plan.v1.schema.json",
            "contracts/canon/aal_viz_geometric_renderer_planning.v1.schema.json",
            "contracts/canon/geometric_projection_spec.v1.schema.json",
            "contracts/canon/metric_operator_registry.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def _build_markdown(packet: dict) -> str:
    scope = packet.get("implementation_scope", {})
    packages = packet.get("renderer_work_packages", [])
    lines = [
        "# P44 AAL-Viz Geometric Renderer Implementation Plan",
        "",
        f"- plan_id: `{packet.get('plan_id', '?')}`",
        f"- plan_type: `{packet.get('plan_type', '?')}`",
        f"- schema_version: `{packet.get('schema_version', '?')}`",
        f"- canonical_hash: `{packet.get('canonical_hash', '?')}`",
        f"- created_at_utc: `{packet.get('created_at_utc', '?')}`",
        "",
        "## Implementation Scope",
        f"- target_renderer_family: `{scope.get('target_renderer_family', '?')}`",
        f"- intended_lane: `{scope.get('intended_lane', '?')}`",
        f"- implementation_stage: `{scope.get('implementation_stage', '?')}`",
        "",
        f"## Renderer Work Packages ({len(packages)})",
    ]
    for pkg in packages:
        lines += [
            f"### {pkg.get('package_id', '?')}",
            f"- name: {pkg.get('package_name', '?')}",
            f"- type: `{pkg.get('package_type', '?')}`",
            f"- status: `{pkg.get('implementation_status', '?')}`",
            f"- description: {pkg.get('description', '')}",
            "",
        ]
    lines += [
        "## Dependency Map",
        *(f"- {k}: `{v}`" for k, v in sorted(packet.get("dependency_map", {}).items())),
        "",
        "## Implementation Constraints",
        *(f"- {k}: `{v}`" for k, v in sorted(packet.get("implementation_constraints", {}).items())),
        "",
        "## Governance",
        "- production_activation: `false`",
        "- valid_for_execution: `false`",
        "- advisory_only: `true` (planning gate only)",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "aal_viz_geometric_renderer_implementation_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_implementation_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_aal_viz_geometric_renderer_implementation_plan(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_aal_viz_geometric_renderer_implementation_plan(packet), encoding="utf-8"
    )
    OUT_PATH.with_suffix(".md").write_text(_build_markdown(packet), encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "aal_viz_geometric_renderer_implementation_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
