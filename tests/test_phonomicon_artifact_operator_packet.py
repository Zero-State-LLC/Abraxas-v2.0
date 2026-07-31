"""Tests for PhonomiconArtifactOperatorPacket.v0 (Notion PATCH-007)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.phonomicon.artifact_operator_packet import (
    build_artifact_operator_packet,
    build_artifact_operator_packet_from_sources,
    build_provenance_chain,
)

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "phonomicon" / "artifact_operator_packet.v0.schema.json"


def test_seeded_artifact_packet():
    pack = build_artifact_operator_packet(
        artifact_id="art_001",
        title="Sigil pulse field",
        source_system="beatoven",
        sources=[
            {"source_id": "intent_1", "source_system": "beatoven"},
            {"source_id": "motif_a", "source_system": "noctis"},
        ],
        felt_alignment=0.8,
        symbolic_alignment=0.7,
        uniqueness=0.6,
        sonic_plan_ref="sonic_plan:xyz",
    )
    assert pack["schema_version"] == "PhonomiconArtifactOperatorPacket.v0"
    assert pack["pipeline_id"] == "phonomicon_artifact"
    assert pack["lane"] == "ARTIFACT_GOVERNANCE"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"
    assert pack["provenance"]["link_count"] == 2
    assert pack["proof_of_resonance"]["proof_status"] == "PROOF_SEEDED"
    assert pack["mint_execution_blocked"] is True
    assert pack["authority"]["mint_execution_allowed"] is False
    assert pack["authority"]["provenance_only"] is True
    assert pack["authority"]["operator_approval_required"] is True
    assert pack["rarity"]["tier"] in {"COMMON", "UNCOMMON", "RARE", "MYTHIC"}

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(pack)


def test_provenance_chain_links():
    chain = build_provenance_chain(
        [
            {"source_id": "a", "source_system": "manual"},
            {"source_id": "b", "source_system": "psyfi"},
        ]
    )
    assert chain["link_count"] == 2
    assert chain["chain"][0]["prev_hash"] == "genesis"
    assert chain["chain"][1]["prev_hash"] == chain["chain"][0]["link_hash"]
    assert chain["chain_root_hash"] == chain["chain"][1]["link_hash"]


def test_empty_provenance_not_computable():
    pack = build_artifact_operator_packet(
        artifact_id="empty",
        title="no sources",
        sources=[],
    )
    assert pack["readiness"] == "NOT_COMPUTABLE"
    assert pack["proof_of_resonance"]["proof_status"] == "NOT_COMPUTABLE"
    assert "EMPTY_PROVENANCE_CHAIN" in pack["blocked_by"]
    assert pack["rarity"]["tier"] == "NOT_COMPUTABLE"


def test_incomplete_resonance():
    pack = build_artifact_operator_packet(
        artifact_id="inc",
        sources=[{"source_id": "s1", "source_system": "manual"}],
    )
    assert pack["proof_of_resonance"]["proof_status"] == "PROOF_INCOMPLETE"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"


def test_deterministic():
    kwargs = dict(
        artifact_id="det",
        title="t",
        sources=[{"source_id": "x", "source_system": "manual"}],
        felt_alignment=0.5,
        symbolic_alignment=0.5,
        uniqueness=0.5,
    )
    assert build_artifact_operator_packet(**kwargs) == build_artifact_operator_packet(
        **kwargs
    )


def test_from_sources_dict():
    art = {
        "artifact_id": "from_dict",
        "title": "export candidate",
        "source_system": "beatoven",
        "sources": [
            {"source_id": "graph_1", "source_system": "beatoven"},
        ],
        "felt_alignment": 0.9,
        "symbolic_alignment": 0.8,
        "uniqueness": 0.85,
        "sonic_plan_ref": "sp:1",
    }
    pack = build_artifact_operator_packet_from_sources(art)
    assert pack["artifact_id"] == "from_dict"
    assert pack["proof_of_resonance"]["proof_status"] == "PROOF_SEEDED"
    assert pack["rarity"]["tier"] in {"RARE", "MYTHIC", "UNCOMMON", "COMMON"}
