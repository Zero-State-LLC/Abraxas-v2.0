from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.belief_graph.belief_graph_builder import build_belief_graph_packet
from core.canonical.json import canonical_dumps


def _packet():
    return build_belief_graph_packet(
        claims=(
            {
                "id": "claim-002",
                "statement": "Observed signal remains unresolved.",
                "provenance": {"lane": "shadow"},
                "evidence_refs": ("ev-001",),
                "confidence": 0.4,
                "status": "OBSERVED",
            },
            {
                "id": "claim-001",
                "statement": "Secondary interpretation remains advisory only.",
                "provenance": {"lane": "shadow"},
                "evidence_refs": ("ev-001",),
                "confidence": "NOT_COMPUTABLE",
                "status": "NOT_COMPUTABLE",
            },
        ),
        evidence=(
            {
                "source": "operator_log",
                "provenance": {"lane": "shadow"},
                "timestamp": "2026-06-02T00:00:00Z",
                "evidence_type": "TEXT",
                "hash": "ev-001",
            },
        ),
        theories=(
            {
                "id": "theory-001",
                "supporting_claims": ("claim-002",),
                "conflicting_claims": ("claim-001",),
                "evidence_refs": ("ev-001",),
            },
        ),
        relationships=(
            {
                "source_ref": "theory-001",
                "source_type": "theory",
                "target_ref": "claim-002",
                "target_type": "claim",
                "relationship": "organizes",
            },
            {
                "source_ref": "claim-002",
                "source_type": "claim",
                "target_ref": "ev-001",
                "target_type": "evidence",
                "relationship": "supported_by",
            },
            {
                "source_ref": "claim-001",
                "source_type": "claim",
                "target_ref": "claim-002",
                "target_type": "claim",
                "relationship": "adjacent_to",
            },
        ),
        provenance={"source": "PATCH-ABX-BELIEF-GRAPH-001"},
    )


def test_belief_graph_packet_is_deterministic() -> None:
    first = _packet()
    second = _packet()
    assert canonical_dumps(first.model_dump(mode="json")) == canonical_dumps(
        second.model_dump(mode="json")
    )


def test_belief_graph_packet_preserves_required_seal_and_not_computable_state() -> None:
    packet = _packet()
    assert packet.shadow_forecast_separation.SHADOW_SURFACE == "SHADOW"
    assert packet.shadow_forecast_separation.FORECAST_SURFACE == "FORECAST"
    assert packet.FORECAST_ROUTING is False
    assert packet.CANON_MUTATION is False
    assert packet.RUNTIME_MUTATION is False
    assert packet.EXECUTION_AUTHORITY is False
    assert packet.TRUTH_ASSIGNMENT is False
    assert packet.BELIEF_PROMOTION is False
    assert packet.FINAL_STATUS == "BELIEF_GRAPH_SCAFFOLD_ADVISORY_ONLY"
    assert packet.claims[0].status == "NOT_COMPUTABLE"
    assert packet.claims[0].confidence == "NOT_COMPUTABLE"


def test_belief_graph_packet_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/belief_graph/belief_graph_packet.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(_packet().model_dump(mode="json"), schema)
