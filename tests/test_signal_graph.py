from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.belief_graph.signal_graph import SignalGraph, SignalGraphRelationship


def test_signal_graph_accepts_allowed_relationship_pairs() -> None:
    graph = SignalGraph(
        relationship_count=3,
        relationships=(
            SignalGraphRelationship(
                source_ref="claim-001",
                source_type="claim",
                target_ref="claim-002",
                target_type="claim",
                relationship="related_to",
            ),
            SignalGraphRelationship(
                source_ref="claim-001",
                source_type="claim",
                target_ref="ev-001",
                target_type="evidence",
                relationship="supported_by",
            ),
            SignalGraphRelationship(
                source_ref="theory-001",
                source_type="theory",
                target_ref="claim-001",
                target_type="claim",
                relationship="organizes",
            ),
        ),
    )
    assert graph.relationship_count == 3


def test_signal_graph_rejects_forbidden_pairs() -> None:
    with pytest.raises(
        ValidationError, match="signal graph only stores claim/evidence/theory relationships"
    ):
        SignalGraphRelationship(
            source_ref="theory-001",
            source_type="theory",
            target_ref="theory-002",
            target_type="theory",
            relationship="competes_with",
        )


def test_signal_graph_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/belief_graph/signal_graph.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    graph = SignalGraph(
        relationship_count=2,
        relationships=(
            SignalGraphRelationship(
                source_ref="claim-001",
                source_type="claim",
                target_ref="ev-001",
                target_type="evidence",
                relationship="supported_by",
            ),
            SignalGraphRelationship(
                source_ref="theory-001",
                source_type="theory",
                target_ref="ev-001",
                target_type="evidence",
                relationship="references",
            ),
        ),
    )
    jsonschema.validate(graph.model_dump(mode="json"), schema)
