import pytest

from core.belief_graph.compositional_memory import (
    CompositionalMemoryEntry,
    build_compositional_memory_packet,
    memory_entry_from_evidence,
)
from core.belief_graph.evidence_object import EvidenceObject


def test_memory_entry_from_evidence_preserves_provenance() -> None:
    evidence = EvidenceObject(
        source="fixture-image",
        provenance={"source": "fixture", "lineage": "artifact-1"},
        timestamp="2026-07-23T00:00:00Z",
        evidence_type="image",
        hash="sha256:image-1",
    )

    entry = memory_entry_from_evidence(
        evidence,
        memory_id="visual-1",
        modality="visual",
        semantic_tags=("signal", "signal", "camera"),
    )

    assert entry.evidence_refs == ("sha256:image-1",)
    assert entry.semantic_tags == ("camera", "signal")
    assert entry.provenance["lineage"] == "artifact-1"


def test_packet_separates_modalities_and_builds_deterministic_connector() -> None:
    entries = [
        CompositionalMemoryEntry(
            memory_id="text-1",
            modality="textual",
            source_ref="claim-1",
            content_hash="sha256:text-1",
            observed_at="2026-07-23T00:00:00Z",
            provenance={"source": "fixture"},
            evidence_refs=("evidence-1",),
            semantic_tags=("camera", "surveillance"),
        ),
        CompositionalMemoryEntry(
            memory_id="visual-1",
            modality="visual",
            source_ref="artifact-1",
            content_hash="sha256:visual-1",
            observed_at="2026-07-23T00:00:00Z",
            provenance={"source": "fixture"},
            evidence_refs=("evidence-1",),
            semantic_tags=("camera",),
        ),
    ]

    first = build_compositional_memory_packet(entries)
    second = build_compositional_memory_packet(list(reversed(entries)))

    assert first == second
    assert first["entry_count"] == 2
    assert first["connector_count"] == 1
    connector = first["knowledge_connectors"][0]
    assert connector["shared_evidence_refs"] == ["evidence-1"]
    assert connector["shared_semantic_tags"] == ["camera"]
    assert first["model_mutation"] is False
    assert first["execution_authority"] is False
    assert first["advisory_only"] is True


def test_packet_rejects_duplicate_memory_ids() -> None:
    entries = [
        {
            "memory_id": "duplicate",
            "modality": "textual",
            "source_ref": "claim-1",
            "content_hash": "sha256:text-1",
            "observed_at": "2026-07-23T00:00:00Z",
            "provenance": {"source": "fixture"},
        },
        {
            "memory_id": "duplicate",
            "modality": "visual",
            "source_ref": "artifact-1",
            "content_hash": "sha256:visual-1",
            "observed_at": "2026-07-23T00:00:00Z",
            "provenance": {"source": "fixture"},
        },
    ]

    with pytest.raises(
        ValueError,
        match="duplicate memory_id values are not allowed",
    ):
        build_compositional_memory_packet(entries)


def test_connector_hash_uses_canonical_structured_data() -> None:
    common = {
        "observed_at": "2026-07-23T00:00:00Z",
        "provenance": {"source": "fixture"},
        "evidence_refs": ["evidence-1"],
    }
    first = build_compositional_memory_packet(
        [
            {
                **common,
                "memory_id": "text|alpha",
                "modality": "textual",
                "source_ref": "claim-1",
                "content_hash": "sha256:text-1",
            },
            {
                **common,
                "memory_id": "visual",
                "modality": "visual",
                "source_ref": "artifact-1",
                "content_hash": "sha256:visual-1",
            },
        ]
    )
    second = build_compositional_memory_packet(
        [
            {
                **common,
                "memory_id": "text",
                "modality": "textual",
                "source_ref": "claim-2",
                "content_hash": "sha256:text-2",
            },
            {
                **common,
                "memory_id": "alpha|visual",
                "modality": "visual",
                "source_ref": "artifact-2",
                "content_hash": "sha256:visual-2",
            },
        ]
    )

    first_hash = first["knowledge_connectors"][0]["connector_hash"]
    second_hash = second["knowledge_connectors"][0]["connector_hash"]
    assert first_hash != second_hash


def test_packet_does_not_invent_connector_without_shared_signal() -> None:
    packet = build_compositional_memory_packet(
        [
            {
                "memory_id": "text-1",
                "modality": "textual",
                "source_ref": "claim-1",
                "content_hash": "sha256:text-1",
                "observed_at": "2026-07-23T00:00:00Z",
                "provenance": {"source": "fixture"},
                "evidence_refs": ["evidence-a"],
                "semantic_tags": ["alpha"],
            },
            {
                "memory_id": "visual-1",
                "modality": "visual",
                "source_ref": "artifact-1",
                "content_hash": "sha256:visual-1",
                "observed_at": "2026-07-23T00:00:00Z",
                "provenance": {"source": "fixture"},
                "evidence_refs": ["evidence-b"],
                "semantic_tags": ["beta"],
            },
        ]
    )

    assert packet["connector_count"] == 0
    assert packet["knowledge_connectors"] == []
    assert packet["truth_assignment"] is False
