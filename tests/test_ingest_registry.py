from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.ingest import DEFAULT_INGEST_REGISTRY, FINAL_STATUS


def test_filesystem_adapter_builds_sealed_belief_graph_packet(tmp_path: Path) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("local observation", encoding="utf-8")

    packet = DEFAULT_INGEST_REGISTRY.ingest(tmp_path, source)
    belief_graph_packet = packet.to_belief_graph_packet()

    assert packet.adapter_id == "filesystem_adapter"
    assert packet.claims[0].status == "OBSERVED"
    assert packet.claims[0].confidence == 0.0
    assert packet.FORECAST_ROUTING is False
    assert packet.CANON_MUTATION is False
    assert packet.RUNTIME_MUTATION is False
    assert packet.EXECUTION_AUTHORITY is False
    assert packet.TRUTH_ASSIGNMENT is False
    assert packet.FINAL_STATUS == FINAL_STATUS
    assert belief_graph_packet.FORECAST_ROUTING is False
    assert belief_graph_packet.CANON_MUTATION is False
    assert belief_graph_packet.RUNTIME_MUTATION is False
    assert belief_graph_packet.EXECUTION_AUTHORITY is False
    assert belief_graph_packet.TRUTH_ASSIGNMENT is False
    assert belief_graph_packet.claims[0].evidence_refs == (
        belief_graph_packet.evidence[0].hash,
    )
    assert belief_graph_packet.theories[0].evidence_refs == (
        belief_graph_packet.evidence[0].hash,
    )


def test_json_adapter_preserves_supported_status_and_confidence(tmp_path: Path) -> None:
    source = tmp_path / "payload.json"
    source.write_text(
        json.dumps(
            {
                "statement": "Speculative interpretation remains advisory.",
                "status": "SPECULATIVE",
                "confidence": 0.25,
            }
        ),
        encoding="utf-8",
    )

    packet = DEFAULT_INGEST_REGISTRY.ingest(tmp_path, source)

    assert packet.adapter_id == "json_adapter"
    assert packet.claims[0].status == "SPECULATIVE"
    assert packet.claims[0].confidence == 0.25


def test_audit_artifact_adapter_defaults_to_inferred_and_preserves_not_computable(
    tmp_path: Path,
) -> None:
    audit_dir = tmp_path / "out" / "audit"
    audit_dir.mkdir(parents=True)
    inferred_path = audit_dir / "artifact.latest.json"
    inferred_path.write_text(
        json.dumps({"schema_version": "Artifact.v1", "summary": "Audit artifact observed."}),
        encoding="utf-8",
    )

    inferred_packet = DEFAULT_INGEST_REGISTRY.ingest(tmp_path, inferred_path)
    assert inferred_packet.adapter_id == "audit_artifact_adapter"
    assert inferred_packet.claims[0].status == "INFERRED"
    assert inferred_packet.claims[0].confidence == 0.0

    not_computable_path = audit_dir / "artifact_not_computable.latest.json"
    not_computable_path.write_text(
        json.dumps({"schema_version": "Artifact.v1", "status": "NOT_COMPUTABLE"}),
        encoding="utf-8",
    )

    not_computable_packet = DEFAULT_INGEST_REGISTRY.ingest(tmp_path, not_computable_path)
    assert not_computable_packet.claims[0].status == "NOT_COMPUTABLE"
    assert not_computable_packet.claims[0].confidence == "NOT_COMPUTABLE"


def test_ingest_rejects_sources_outside_repository_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="local repository sources"):
        DEFAULT_INGEST_REGISTRY.ingest(tmp_path, outside)
