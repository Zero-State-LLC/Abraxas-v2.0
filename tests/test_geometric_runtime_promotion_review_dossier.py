from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geometric_runtime_promotion_review_dossier import (
    build_geometric_runtime_promotion_review_dossier,
    compute_geometric_runtime_promotion_review_dossier_hash,
    default_blocker_findings,
    default_output_contract,
    default_promotion_constraints,
    default_readiness_findings,
    default_review_decision,
    serialize_geometric_runtime_promotion_review_dossier,
)


def _payload() -> dict[str, object]:
    return {
        "dossier_id": "geometric-runtime-promotion-review-dossier-001",
        "source_archive_receipt_refs": ["REPO_FINAL_ARCHIVE_RECEIPT_GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1"],
        "source_renderer_plan_refs": ["AALVizGeometricRendererImplementationPlan.v1:plan-001"],
        "source_metric_selection_plan_refs": ["MetricOperatorImplementationSelectionPlan.v1:plan-001"],
        "source_oracle_stabilization_window_refs": ["OracleGeometricAttachmentStabilizationWindow.v1:window-001"],
        "source_yggdrasil_stabilization_window_refs": ["YggdrasilGeometricRouteStabilizationWindow.v1:window-001"],
        "review_scope": {
            "reviewed_runtime": "GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1",
            "review_stage": "PROMOTION_REVIEW_ONLY",
            "intended_lane": "REVIEW",
        },
        "readiness_findings": default_readiness_findings(),
        "blocker_findings": default_blocker_findings(),
        "promotion_constraints": default_promotion_constraints(),
        "review_decision": default_review_decision(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
        )},
        "provenance": {
            "source": "GEOMETRIC_REVIEW_DOSSIER_v0.1_boundary_opening",
            "evidence_refs": [
                "REPO_FINAL_ARCHIVE_RECEIPT_GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1",
                "AALVizGeometricRendererImplementationPlan.v1:plan-001",
                "MetricOperatorImplementationSelectionPlan.v1:plan-001",
                "OracleGeometricAttachmentStabilizationWindow.v1:window-001",
                "YggdrasilGeometricRouteStabilizationWindow.v1:window-001",
            ],
            "generated_by": "unit-test",
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer_implementation_plan.v1.schema.json",
                "contracts/canon/metric_operator_implementation_selection_plan.v1.schema.json",
                "contracts/canon/oracle_geometric_attachment_stabilization_window.v1.schema.json",
                "contracts/canon/yggdrasil_geometric_route_stabilization_window.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    a = build_geometric_runtime_promotion_review_dossier(_payload())
    b = build_geometric_runtime_promotion_review_dossier(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_geometric_runtime_promotion_review_dossier(a) == serialize_geometric_runtime_promotion_review_dossier(b)


def test_defaults_non_empty_and_deterministic() -> None:
    assert default_readiness_findings()
    assert default_blocker_findings()
    assert default_readiness_findings() == default_readiness_findings()
    assert default_blocker_findings() == default_blocker_findings()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["readiness_findings"].append(dict(p["readiness_findings"][0])), "duplicate_finding_id"),
        (lambda p: p["blocker_findings"].append(dict(p["blocker_findings"][0])), "duplicate_blocker_id"),
        (lambda p: p["review_scope"].__setitem__("reviewed_runtime", "BAD"), "unknown_reviewed_runtime"),
        (lambda p: p["review_scope"].__setitem__("review_stage", "BAD"), "unknown_review_stage"),
        (lambda p: p["review_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["readiness_findings"][0].__setitem__("finding_type", "BAD"), "unknown_finding_type"),
        (lambda p: p["readiness_findings"][0].__setitem__("readiness_status", "BAD"), "unknown_readiness_status"),
        (lambda p: p["readiness_findings"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
        (lambda p: p["blocker_findings"][0].__setitem__("blocker_type", "BAD"), "unknown_blocker_type"),
        (lambda p: p["blocker_findings"][0].__setitem__("blocker_status", "BAD"), "unknown_blocker_status"),
    ],
)
def test_invalid_enums(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_geometric_runtime_promotion_review_dossier(payload)


def test_locked_maps_and_flags() -> None:
    for key in default_promotion_constraints().keys():
        payload = _payload()
        payload["promotion_constraints"][key] = True
        with pytest.raises(ValueError, match="invalid_promotion_constraints"):
            build_geometric_runtime_promotion_review_dossier(payload)

    for key in default_review_decision().keys():
        payload = _payload()
        if isinstance(payload["review_decision"][key], bool):
            payload["review_decision"][key] = not payload["review_decision"][key]
        else:
            payload["review_decision"][key] = "BAD"
        with pytest.raises(ValueError, match="invalid_review_decision"):
            build_geometric_runtime_promotion_review_dossier(payload)

    for key in ("emits_promotion", "emits_activation", "emits_runtime_controls", "emits_forecast_inputs", "emits_authority_tokens"):
        payload = _payload()
        payload["output_contract"][key] = True
        with pytest.raises(ValueError, match="invalid_output_contract"):
            build_geometric_runtime_promotion_review_dossier(payload)

    payload = _payload()
    payload["governance_flags"]["canon_promotion"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_geometric_runtime_promotion_review_dossier(payload)


def test_provenance_forbidden_tokens_rejected() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime scheduler cache forecast scoring promotion activation authorization canon-mutation"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_geometric_runtime_promotion_review_dossier(payload)


def test_hash_excludes_canonical_hash_and_changes_on_meaningful_change() -> None:
    packet = build_geometric_runtime_promotion_review_dossier(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_geometric_runtime_promotion_review_dossier_hash(packet) == compute_geometric_runtime_promotion_review_dossier_hash(altered)

    changed_payload = _payload()
    changed_payload["review_scope"]["review_stage"] = "READINESS_ASSESSMENT_ONLY"
    changed = build_geometric_runtime_promotion_review_dossier(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/geometric_runtime_promotion_review_dossier.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(build_geometric_runtime_promotion_review_dossier(_payload()), schema)


def test_references_are_id_only_strings() -> None:
    packet = build_geometric_runtime_promotion_review_dossier(_payload())
    refs = (
        packet["source_archive_receipt_refs"]
        + packet["source_renderer_plan_refs"]
        + packet["source_metric_selection_plan_refs"]
        + packet["source_oracle_stabilization_window_refs"]
        + packet["source_yggdrasil_stabilization_window_refs"]
    )
    assert all(isinstance(r, str) for r in refs)
