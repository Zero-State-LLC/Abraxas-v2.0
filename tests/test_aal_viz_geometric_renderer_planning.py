from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.aal_viz_geometric_renderer_planning import (
    build_aal_viz_geometric_renderer_planning,
    compute_aal_viz_geometric_renderer_planning_hash,
    default_implementation_gates,
    default_output_contract,
    default_planned_surfaces,
    default_renderer_constraints,
    serialize_aal_viz_geometric_renderer_planning,
)


def _payload() -> dict[str, object]:
    return {
        "planning_id": "aal-viz-geometric-renderer-planning-001",
        "source_projection_spec_refs": ["GeometricProjectionSpec.v1:projection-spec-001"],
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "source_test_vector_pack_refs": ["MetricOperatorBaselineTestVectorPack.v1:pack-001"],
        "source_oracle_replay_receipt_refs": ["OracleGeometricAttachmentReplayReceipt.v1:receipt-001"],
        "source_yggdrasil_replay_receipt_refs": ["YggdrasilGeometricRouteReplayReceipt.v1:receipt-001"],
        "renderer_scope": {
            "target_surface_family": "MULTI_SURFACE_PLANNING",
            "intended_lane": "PROJECTION",
            "planning_stage": "IMPLEMENTATION_PLANNING_ONLY",
        },
        "planned_surfaces": default_planned_surfaces(),
        "renderer_constraints": default_renderer_constraints(),
        "implementation_gates": default_implementation_gates(),
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
            "source": "GI_RENDER_PLAN_v0.1_patch14",
            "evidence_refs": ["contracts/canon/geometric_projection_spec.v1.schema.json"],
            "generated_by": "unit-test",
            "upstream_schema_refs": [
                "contracts/canon/geometric_projection_spec.v1.schema.json",
                "contracts/canon/metric_operator_registry.v1.schema.json",
                "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
                "contracts/canon/oracle_geometric_attachment_replay_receipt.v1.schema.json",
                "contracts/canon/yggdrasil_geometric_route_replay_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-27T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    a = build_aal_viz_geometric_renderer_planning(_payload())
    b = build_aal_viz_geometric_renderer_planning(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_aal_viz_geometric_renderer_planning(a) == serialize_aal_viz_geometric_renderer_planning(b)


def test_default_planned_surfaces_non_empty_and_deterministic() -> None:
    assert default_planned_surfaces()
    assert default_planned_surfaces() == default_planned_surfaces()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["planned_surfaces"].append(dict(p["planned_surfaces"][0])), "duplicate_surface_id"),
        (lambda p: p["renderer_scope"].__setitem__("target_surface_family", "BAD"), "unknown_target_surface_family"),
        (lambda p: p["renderer_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["renderer_scope"].__setitem__("planning_stage", "BAD"), "unknown_planning_stage"),
        (lambda p: p["planned_surfaces"][0].__setitem__("surface_family", "BAD"), "unknown_surface_family"),
        (lambda p: p["planned_surfaces"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
        (lambda p: p["planned_surfaces"][0].__setitem__("evidence_required", "BAD"), "unknown_evidence_required"),
    ],
)
def test_invalid_enums(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_aal_viz_geometric_renderer_planning(payload)


def test_constraint_gate_contract_locks_and_governance_locks() -> None:
    for key in default_renderer_constraints().keys():
        payload = _payload()
        payload["renderer_constraints"][key] = True
        with pytest.raises(ValueError, match="invalid_renderer_constraints"):
            build_aal_viz_geometric_renderer_planning(payload)

    for key in default_implementation_gates().keys():
        payload = _payload()
        payload["implementation_gates"][key] = False
        with pytest.raises(ValueError, match="invalid_implementation_gates"):
            build_aal_viz_geometric_renderer_planning(payload)

    for key in ("emits_rendered_output", "emits_ui_controls", "emits_metric_values", "emits_forecast_inputs", "emits_runtime_controls", "emits_authority_tokens"):
        payload = _payload()
        payload["output_contract"][key] = True
        with pytest.raises(ValueError, match="invalid_output_contract"):
            build_aal_viz_geometric_renderer_planning(payload)

    payload = _payload()
    payload["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_aal_viz_geometric_renderer_planning(payload)


def test_provenance_forbidden_tokens_rejected() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime scheduler cache forecast rendering ui svg webgl canvas metric-computation route-control"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_aal_viz_geometric_renderer_planning(payload)


def test_hash_excludes_canonical_hash_and_changes_on_meaningful_change() -> None:
    packet = build_aal_viz_geometric_renderer_planning(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_aal_viz_geometric_renderer_planning_hash(packet) == compute_aal_viz_geometric_renderer_planning_hash(altered)

    changed_payload = _payload()
    changed_payload["renderer_scope"]["planning_stage"] = "CONTRACT_ONLY"
    changed = build_aal_viz_geometric_renderer_planning(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/aal_viz_geometric_renderer_planning.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(build_aal_viz_geometric_renderer_planning(_payload()), schema)


def test_references_are_id_only_strings() -> None:
    packet = build_aal_viz_geometric_renderer_planning(_payload())
    refs = (
        packet["source_projection_spec_refs"]
        + packet["source_metric_registry_refs"]
        + packet["source_test_vector_pack_refs"]
        + packet["source_oracle_replay_receipt_refs"]
        + packet["source_yggdrasil_replay_receipt_refs"]
    )
    assert all(isinstance(r, str) for r in refs)
