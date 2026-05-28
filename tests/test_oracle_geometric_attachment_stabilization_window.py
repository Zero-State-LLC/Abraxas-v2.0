from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.oracle_geometric_attachment_stabilization_window import (
    build_oracle_geometric_attachment_stabilization_window,
    compute_oracle_geometric_attachment_stabilization_window_hash,
    default_observation_requirements,
    default_oracle_effects,
    default_output_contract,
    default_replay_effects,
    default_stability_expectations,
    default_window_constraints,
    serialize_oracle_geometric_attachment_stabilization_window,
)


def _payload() -> dict[str, object]:
    return {
        "window_id": "oracle-geometric-attachment-stabilization-window-001",
        "source_attachment_refs": ["OracleGeometricSignalAttachment.v1:item-001"],
        "source_replay_receipt_refs": ["OracleGeometricAttachmentReplayReceipt.v1:receipt-001"],
        "source_signal_packet_refs": ["GeometricSignalPacket.v1:item-001"],
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "stabilization_scope": {
            "surface_type": "ORACLE_GEOMETRIC_ATTACHMENT_REPLAY_RECEIPT",
            "window_mode": "STABILIZATION_DECLARED_ONLY",
            "intended_lane": "OBSERVATION_ONLY",
            "observation_window": "shadow-window-001",
        },
        "observation_requirements": default_observation_requirements(),
        "stability_expectations": default_stability_expectations(),
        "window_constraints": default_window_constraints(),
        "oracle_effects": default_oracle_effects(),
        "replay_effects": default_replay_effects(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
        )},
        "provenance": {
            "source": "ORACLE_STABILIZATION_WINDOW_v0.1_boundary_opening",
            "evidence_refs": [
                "OracleGeometricSignalAttachment.v1:item-001",
                "OracleGeometricAttachmentReplayReceipt.v1:receipt-001",
                "GeometricSignalPacket.v1:item-001",
                "MetricOperatorRegistry.v1:registry-001",
            ],
            "generated_by": "unit-test",
            "upstream_schema_refs": [
                "contracts/canon/oracle_geometric_signal_attachment.v1.schema.json",
                "contracts/canon/oracle_geometric_attachment_replay_receipt.v1.schema.json",
                "contracts/canon/geometric_signal_packet.v1.schema.json",
                "contracts/canon/metric_operator_registry.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    a = build_oracle_geometric_attachment_stabilization_window(_payload())
    b = build_oracle_geometric_attachment_stabilization_window(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_oracle_geometric_attachment_stabilization_window(a) == serialize_oracle_geometric_attachment_stabilization_window(b)


def test_default_observation_requirements_non_empty_and_deterministic() -> None:
    assert default_observation_requirements()
    assert default_observation_requirements() == default_observation_requirements()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["observation_requirements"].append(dict(p["observation_requirements"][0])), "duplicate_requirement_id"),
        (lambda p: p["stabilization_scope"].__setitem__("surface_type", "BAD"), "unknown_surface_type"),
        (lambda p: p["stabilization_scope"].__setitem__("window_mode", "BAD"), "unknown_window_mode"),
        (lambda p: p["stabilization_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["observation_requirements"][0].__setitem__("requirement_type", "BAD"), "unknown_requirement_type"),
        (lambda p: p["observation_requirements"][0].__setitem__("evidence_required", "BAD"), "unknown_evidence_required"),
        (lambda p: p["observation_requirements"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
    ],
)
def test_invalid_enums(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_oracle_geometric_attachment_stabilization_window(payload)


def test_locked_maps_and_flags() -> None:
    for key in default_stability_expectations().keys():
        payload = _payload()
        payload["stability_expectations"][key] = not payload["stability_expectations"][key]
        with pytest.raises(ValueError, match="invalid_stability_expectations"):
            build_oracle_geometric_attachment_stabilization_window(payload)

    for key in default_window_constraints().keys():
        payload = _payload()
        payload["window_constraints"][key] = True
        with pytest.raises(ValueError, match="invalid_window_constraints"):
            build_oracle_geometric_attachment_stabilization_window(payload)

    for key in default_oracle_effects().keys():
        payload = _payload()
        payload["oracle_effects"][key] = True
        with pytest.raises(ValueError, match="invalid_oracle_effects"):
            build_oracle_geometric_attachment_stabilization_window(payload)

    for key in default_replay_effects().keys():
        payload = _payload()
        payload["replay_effects"][key] = True
        with pytest.raises(ValueError, match="invalid_replay_effects"):
            build_oracle_geometric_attachment_stabilization_window(payload)

    for key in ("emits_stability_scores", "emits_oracle_scores", "emits_forecast_inputs", "emits_runtime_controls", "emits_authority_tokens"):
        payload = _payload()
        payload["output_contract"][key] = True
        with pytest.raises(ValueError, match="invalid_output_contract"):
            build_oracle_geometric_attachment_stabilization_window(payload)

    payload = _payload()
    payload["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_oracle_geometric_attachment_stabilization_window(payload)


def test_provenance_forbidden_tokens_rejected() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime scheduler cache forecast scoring oracle-score replay-execution stabilization-execution route-selection"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_oracle_geometric_attachment_stabilization_window(payload)


def test_hash_excludes_canonical_hash_and_changes_on_meaningful_change() -> None:
    packet = build_oracle_geometric_attachment_stabilization_window(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_oracle_geometric_attachment_stabilization_window_hash(packet) == compute_oracle_geometric_attachment_stabilization_window_hash(altered)

    changed_payload = _payload()
    changed_payload["stabilization_scope"]["window_mode"] = "HASH_STABILITY_WINDOW"
    changed = build_oracle_geometric_attachment_stabilization_window(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/oracle_geometric_attachment_stabilization_window.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(build_oracle_geometric_attachment_stabilization_window(_payload()), schema)


def test_references_are_id_only_strings() -> None:
    packet = build_oracle_geometric_attachment_stabilization_window(_payload())
    refs = (
        packet["source_attachment_refs"]
        + packet["source_replay_receipt_refs"]
        + packet["source_signal_packet_refs"]
        + packet["source_metric_registry_refs"]
    )
    assert all(isinstance(r, str) for r in refs)
