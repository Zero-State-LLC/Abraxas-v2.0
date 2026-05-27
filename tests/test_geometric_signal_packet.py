from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geometric_signal_packet import (
    build_geometric_signal_packet,
    canonicalize_geometric_signal_packet,
    compute_geometric_signal_packet_hash,
    serialize_geometric_signal_packet,
    validate_geometric_signal_packet,
)


def _base_packet() -> dict:
    return build_geometric_signal_packet(
        packet_id="GSP-0001",
        source_research_item_ids=["GRI-abc123"],
        observed_signal_summary="shadow-only geometric observation",
        geometric_concepts=["manifold", "curvature"],
        metric_placeholders=["WASSERSTEIN", "GEODESIC"],
        architecture_targets=["ORACLE_SIGNAL_LAYER", "GEOMETRIC_INTELLIGENCE_RUNTIME"],
        classification="SHADOW_ONLY",
        provenance={
            "source": "oracle-shadow",
            "evidence_refs": ["out/research_shadow_replay_audit/latest.json"],
            "generated_by": "test-suite",
            "upstream_schema_refs": ["contracts/canon/geometric_research_item.v1.schema.json"],
        },
        created_at_utc="2026-05-27T00:00:00Z",
    )


def test_valid_packet_deterministic_hash() -> None:
    first = _base_packet()
    second = _base_packet()
    assert first["canonical_hash"] == second["canonical_hash"]


def test_repeated_serialization_byte_stable() -> None:
    packet = _base_packet()
    assert serialize_geometric_signal_packet(packet) == serialize_geometric_signal_packet(packet)


def test_source_ids_non_empty() -> None:
    with pytest.raises(ValueError, match="source_research_item_ids"):
        canonicalize_geometric_signal_packet({**_base_packet(), "source_research_item_ids": []})


def test_unknown_classification_fails() -> None:
    with pytest.raises(ValueError, match="unknown classification"):
        canonicalize_geometric_signal_packet({**_base_packet(), "classification": "NOPE"})


def test_unknown_architecture_target_fails() -> None:
    with pytest.raises(ValueError, match="unknown architecture target"):
        canonicalize_geometric_signal_packet({**_base_packet(), "architecture_targets": ["NOPE"]})


def test_unknown_metric_placeholder_fails() -> None:
    with pytest.raises(ValueError, match="unknown metric placeholder"):
        canonicalize_geometric_signal_packet({**_base_packet(), "metric_placeholders": ["NOPE"]})


def test_shadow_observation_invariants() -> None:
    with pytest.raises(ValueError, match="shadow_observation.observation_only"):
        canonicalize_geometric_signal_packet({**_base_packet(), "shadow_observation": {**_base_packet()["shadow_observation"], "observation_only": False}})


def test_governance_flags_cannot_be_true() -> None:
    bad = _base_packet()
    bad["governance_flags"] = {**bad["governance_flags"], "forecast_influence": True}
    with pytest.raises(ValueError, match="governance_flags.forecast_influence"):
        canonicalize_geometric_signal_packet(bad)


def test_hash_excludes_canonical_hash_preimage() -> None:
    packet = _base_packet()
    changed = {**packet, "canonical_hash": "0" * 64}
    assert compute_geometric_signal_packet_hash(changed) == packet["canonical_hash"]


def test_hash_changes_on_content_change() -> None:
    packet = _base_packet()
    changed = canonicalize_geometric_signal_packet({**packet, "observed_signal_summary": "changed"})
    assert changed["canonical_hash"] != packet["canonical_hash"]


def test_schema_validation_if_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/geometric_signal_packet.v1.schema.json").read_text())
    jsonschema.validate(_base_packet(), schema)


def test_reference_research_item_id_only() -> None:
    packet = _base_packet()
    assert packet["source_research_item_ids"] == ["GRI-abc123"]
    validate_geometric_signal_packet(packet)
