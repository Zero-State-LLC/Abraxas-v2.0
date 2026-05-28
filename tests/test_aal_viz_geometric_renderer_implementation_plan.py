from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.aal_viz_geometric_renderer_implementation_plan import (
    build_aal_viz_geometric_renderer_implementation_plan,
    compute_aal_viz_geometric_renderer_implementation_plan_hash,
    default_dependency_map,
    default_implementation_constraints,
    default_output_contract,
    default_renderer_work_packages,
    default_validation_plan,
    serialize_aal_viz_geometric_renderer_implementation_plan,
)


def _payload() -> dict[str, object]:
    return {
        "plan_id": "aal-viz-geometric-renderer-implementation-plan-001",
        "source_renderer_planning_refs": ["AALVizGeometricRendererPlanning.v1:planning-001"],
        "source_projection_spec_refs": ["GeometricProjectionSpec.v1:projection-spec-001"],
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "source_test_vector_pack_refs": ["MetricOperatorBaselineTestVectorPack.v1:pack-001"],
        "implementation_scope": {
            "target_renderer_family": "MULTI_SURFACE_RENDERER_PLANNING",
            "intended_lane": "PROJECTION",
            "implementation_stage": "IMPLEMENTATION_PLAN_ONLY",
        },
        "renderer_work_packages": default_renderer_work_packages(),
        "dependency_map": default_dependency_map(),
        "implementation_constraints": default_implementation_constraints(),
        "validation_plan": default_validation_plan(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
        )},
        "provenance": {
            "source": "GI_RENDER_PLAN_v0.1_boundary_opening",
            "evidence_refs": [
                "AALVizGeometricRendererPlanning.v1:planning-001",
                "GeometricProjectionSpec.v1:projection-spec-001",
                "MetricOperatorBaselineTestVectorPack.v1:pack-001",
                "OracleGeometricAttachmentReplayReceipt.v1:receipt-001",
                "YggdrasilGeometricRouteReplayReceipt.v1:receipt-001",
            ],
            "generated_by": "unit-test",
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer_planning.v1.schema.json",
                "contracts/canon/geometric_projection_spec.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-27T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    a = build_aal_viz_geometric_renderer_implementation_plan(_payload())
    b = build_aal_viz_geometric_renderer_implementation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_aal_viz_geometric_renderer_implementation_plan(a) == serialize_aal_viz_geometric_renderer_implementation_plan(b)


def test_default_work_packages_non_empty_and_deterministic() -> None:
    assert default_renderer_work_packages()
    assert default_renderer_work_packages() == default_renderer_work_packages()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["renderer_work_packages"].append(dict(p["renderer_work_packages"][0])), "duplicate_package_id"),
        (lambda p: p["implementation_scope"].__setitem__("target_renderer_family", "BAD"), "unknown_target_renderer_family"),
        (lambda p: p["implementation_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["implementation_scope"].__setitem__("implementation_stage", "BAD"), "unknown_implementation_stage"),
        (lambda p: p["renderer_work_packages"][0].__setitem__("package_type", "BAD"), "unknown_package_type"),
        (lambda p: p["renderer_work_packages"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
    ],
)
def test_invalid_enums(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_aal_viz_geometric_renderer_implementation_plan(payload)


def test_locked_maps_and_flags() -> None:
    for key in default_dependency_map().keys():
        payload = _payload()
        payload["dependency_map"][key] = False
        with pytest.raises(ValueError, match="invalid_dependency_map"):
            build_aal_viz_geometric_renderer_implementation_plan(payload)

    for key in default_implementation_constraints().keys():
        payload = _payload()
        payload["implementation_constraints"][key] = True
        with pytest.raises(ValueError, match="invalid_implementation_constraints"):
            build_aal_viz_geometric_renderer_implementation_plan(payload)

    for key in default_validation_plan().keys():
        payload = _payload()
        payload["validation_plan"][key] = False
        with pytest.raises(ValueError, match="invalid_validation_plan"):
            build_aal_viz_geometric_renderer_implementation_plan(payload)

    for key in ("emits_code", "emits_rendered_output", "emits_ui_controls", "emits_metric_values", "emits_forecast_inputs", "emits_runtime_controls", "emits_authority_tokens"):
        payload = _payload()
        payload["output_contract"][key] = True
        with pytest.raises(ValueError, match="invalid_output_contract"):
            build_aal_viz_geometric_renderer_implementation_plan(payload)

    payload = _payload()
    payload["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_aal_viz_geometric_renderer_implementation_plan(payload)


def test_provenance_forbidden_tokens_rejected() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime scheduler cache forecast rendering ui svg webgl canvas metric-computation route-control executable"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_aal_viz_geometric_renderer_implementation_plan(payload)


def test_hash_excludes_canonical_hash_and_changes_on_meaningful_change() -> None:
    packet = build_aal_viz_geometric_renderer_implementation_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_aal_viz_geometric_renderer_implementation_plan_hash(packet) == compute_aal_viz_geometric_renderer_implementation_plan_hash(altered)

    changed_payload = _payload()
    changed_payload["implementation_scope"]["implementation_stage"] = "VALIDATION_PLAN_ONLY"
    changed = build_aal_viz_geometric_renderer_implementation_plan(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/aal_viz_geometric_renderer_implementation_plan.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(build_aal_viz_geometric_renderer_implementation_plan(_payload()), schema)


def test_references_are_id_only_strings() -> None:
    packet = build_aal_viz_geometric_renderer_implementation_plan(_payload())
    refs = (
        packet["source_renderer_planning_refs"]
        + packet["source_projection_spec_refs"]
        + packet["source_metric_registry_refs"]
        + packet["source_test_vector_pack_refs"]
        + packet["provenance"]["evidence_refs"]
    )
    assert all(isinstance(r, str) for r in refs)
