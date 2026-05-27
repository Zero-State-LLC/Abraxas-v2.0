from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.yggdrasil_geometric_route_replay_receipt import (
    build_yggdrasil_geometric_route_replay_receipt,
    compute_yggdrasil_geometric_route_replay_receipt_hash,
    default_output_contract,
    default_replay_effects,
    default_replay_observations,
    default_route_effects,
    default_stability_policy,
    serialize_yggdrasil_geometric_route_replay_receipt,
)


def _payload() -> dict[str, object]:
    return {
        "receipt_id": "yggdrasil-geom-route-replay-receipt-001",
        "source_route_metadata_refs": ["YggdrasilGeometricRouteMetadata.v1:route-metadata-001"],
        "source_signal_packet_refs": ["GeometricSignalPacket.v1:signal-packet-001"],
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "source_test_vector_pack_refs": ["MetricOperatorBaselineTestVectorPack.v1:pack-001"],
        "replay_scope": {"surface_type": "YGGDRASIL_GEOMETRIC_ROUTE_METADATA", "replay_mode": "METADATA_REPLAY", "intended_lane": "REPLAY"},
        "replay_observations": default_replay_observations(),
        "stability_policy": default_stability_policy(),
        "route_effects": default_route_effects(),
        "replay_effects": default_replay_effects(),
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
            "source": "GI_ROUTE_RCP_v0.1_patch13",
            "evidence_refs": ["contracts/canon/yggdrasil_geometric_route_metadata.v1.schema.json"],
            "generated_by": "unit-test",
            "upstream_schema_refs": [
                "contracts/canon/yggdrasil_geometric_route_metadata.v1.schema.json",
                "contracts/canon/geometric_signal_packet.v1.schema.json",
                "contracts/canon/metric_operator_registry.v1.schema.json",
                "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-27T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    a = build_yggdrasil_geometric_route_replay_receipt(_payload())
    b = build_yggdrasil_geometric_route_replay_receipt(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_yggdrasil_geometric_route_replay_receipt(a) == serialize_yggdrasil_geometric_route_replay_receipt(b)


def test_default_observations_non_empty_and_deterministic() -> None:
    assert default_replay_observations()
    assert default_replay_observations() == default_replay_observations()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["replay_observations"].append(dict(p["replay_observations"][0])), "duplicate_observation_id"),
        (lambda p: p["replay_scope"].__setitem__("surface_type", "BAD"), "unknown_surface_type"),
        (lambda p: p["replay_scope"].__setitem__("replay_mode", "BAD"), "unknown_replay_mode"),
        (lambda p: p["replay_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["replay_observations"][0].__setitem__("observation_type", "BAD"), "unknown_observation_type"),
        (lambda p: p["replay_observations"][0].__setitem__("evidence_required", "BAD"), "unknown_evidence_required"),
        (lambda p: p["replay_observations"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
    ],
)
def test_invalid_enums(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_yggdrasil_geometric_route_replay_receipt(payload)


def test_policy_and_effect_and_governance_locks() -> None:
    for k in ("replay_execution_enabled", "route_graph_recomputed"):
        payload = _payload()
        payload["stability_policy"][k] = True
        with pytest.raises(ValueError, match="invalid_stability_policy"):
            build_yggdrasil_geometric_route_replay_receipt(payload)

    payload = _payload()
    payload["route_effects"]["affects_route_selection"] = True
    with pytest.raises(ValueError, match="invalid_route_effects"):
        build_yggdrasil_geometric_route_replay_receipt(payload)

    payload = _payload()
    payload["replay_effects"]["executes_replay"] = True
    with pytest.raises(ValueError, match="invalid_replay_effects"):
        build_yggdrasil_geometric_route_replay_receipt(payload)

    payload = _payload()
    payload["output_contract"]["emits_route_scores"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_yggdrasil_geometric_route_replay_receipt(payload)

    payload = _payload()
    payload["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_yggdrasil_geometric_route_replay_receipt(payload)


def test_provenance_forbidden_tokens_rejected() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime scheduler cache forecast scoring route-selection route-scoring graph-replay replay-execution"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_yggdrasil_geometric_route_replay_receipt(payload)


def test_hash_excludes_canonical_hash_and_changes_on_meaningful_change() -> None:
    receipt = build_yggdrasil_geometric_route_replay_receipt(_payload())
    altered = dict(receipt)
    altered["canonical_hash"] = "0" * 64
    assert compute_yggdrasil_geometric_route_replay_receipt_hash(receipt) == compute_yggdrasil_geometric_route_replay_receipt_hash(altered)

    changed_payload = _payload()
    changed_payload["replay_scope"]["replay_mode"] = "HASH_STABILITY_REPLAY"
    changed = build_yggdrasil_geometric_route_replay_receipt(changed_payload)
    assert receipt["canonical_hash"] != changed["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/yggdrasil_geometric_route_replay_receipt.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(build_yggdrasil_geometric_route_replay_receipt(_payload()), schema)


def test_references_are_id_only_strings() -> None:
    receipt = build_yggdrasil_geometric_route_replay_receipt(_payload())
    refs = (
        receipt["source_route_metadata_refs"]
        + receipt["source_signal_packet_refs"]
        + receipt["source_metric_registry_refs"]
        + receipt["source_test_vector_pack_refs"]
    )
    assert all(isinstance(r, str) for r in refs)
