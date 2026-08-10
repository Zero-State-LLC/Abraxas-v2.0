import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.instantiation import (
    DIMENSIONS,
    build_rdi_live_wire_artifact,
    derive_rdi_live_wire_window,
)


def _pack() -> dict:
    return {
        "schema_version": "EvidencePack.v0",
        "pack_id": "evidence-pack-rdi",
        "topic": "RDI",
        "intent": "research",
        "time_horizon": "2026-08-01/2026-08-10",
        "must_answer": [],
        "sources": [
            {"source_id": "s1", "url_or_path": "fixture", "title": "one", "source_class": "code", "excerpt": "x"},
            {"source_id": "s2", "url_or_path": "fixture", "title": "two", "source_class": "code", "excerpt": "y"},
        ],
        "claims": [
            {"claim_id": "c-observed", "dimension": "symbolic_persistence", "text": "x", "register": "OBSERVED", "source_ids": ["s1"]},
            {"claim_id": "c-inferred", "dimension": "recursive_reinforcement", "text": "y", "register": "INFERRED", "source_ids": ["s1", "s2"], "join_logic": "fixture"},
            {"claim_id": "c-speculative", "dimension": "cognitive_penetration", "text": "z", "register": "SPECULATIVE", "source_ids": []},
            {"claim_id": "c-not-computable", "dimension": "material_consequence", "text": "n", "register": "NOT_COMPUTABLE", "source_ids": []},
        ],
        "authority": {"execution_authority": False, "promotion_authorized": False, "forecast_routing_authorized": False, "canon_mutation_allowed": False},
        "provenance": {"producer_system": "OPERATOR", "skill_id": "abx-familiar-signal-forager", "tool_trace_summary": "fixture"},
    }


def _objects() -> list[dict]:
    return [
        {"schema_version": "EvidenceObject.v1", "source": "s1", "timestamp": "2026-08-05T00:00:00Z", "provenance": {}, "evidence_type": "fixture", "hash": "h1"},
        {"schema_version": "EvidenceObject.v1", "source": "s2", "timestamp": "2026-08-06T00:00:00Z", "provenance": {}, "evidence_type": "fixture", "hash": "h2"},
        {"schema_version": "EvidenceObject.v1", "source": "s1", "timestamp": "2026-08-20T00:00:00Z", "provenance": {}, "evidence_type": "fixture", "hash": "h3"},
    ]


def test_window_uses_horizon_and_object_timestamps() -> None:
    window = derive_rdi_live_wire_window(_pack(), _objects())
    assert window["start"] == "2026-08-01T00:00:00+00:00"
    assert window["end"] == "2026-08-10T00:00:00+00:00"
    assert window["evidence_object_timestamps"] == ["2026-08-05T00:00:00Z", "2026-08-06T00:00:00Z"]


def test_live_wire_filters_registers_and_writes_hashed_artifact(tmp_path: Path) -> None:
    artifact = build_rdi_live_wire_artifact(_pack(), _objects(), artifact_id="run-1", out_root=tmp_path)
    assert {claim["claim_id"] for claim in artifact["selected_claims"]} == {"c-observed", "c-inferred"}
    packet = artifact["construct_packet"]
    assert packet["construct"] == "RDI instantiation vector H"
    assert packet["construct_status"] == "EMERGENT"
    assert packet["variable_class"] == "HYBRID"
    assert packet["dimensions"] == list(DIMENSIONS)
    assert packet["route"] == "EVIDENCE_RETRIEVAL"
    path = tmp_path / "rdi_instantiation_shadow" / "run-1.json"
    assert path.is_file()
    saved = json.loads(path.read_text())
    assert saved["canonical_hash"] == canonical_hash({k: v for k, v in saved.items() if k != "canonical_hash"})


def test_live_wire_has_no_console_feed_dependency() -> None:
    source = Path("core/instantiation/shadow.py").read_text()
    assert "aal_viz" not in source.lower()
    assert "console_feed" not in source.lower()
