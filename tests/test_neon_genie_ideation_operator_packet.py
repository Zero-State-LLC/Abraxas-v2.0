"""Tests for neon_genie_ideation operator packet (Track B contract)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from core.neon_genie.ideation_operator_packet import (
    SCHEMA_VERSION,
    build_ideation_operator_packet,
    build_ideation_operator_packet_from_venture,
)

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "neon_genie" / "ideation_operator_packet.v0.schema.json"


def test_schema_loads():
    data = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert data["title"] == "NeonGenieIdeationOperatorPacket.v0"


def test_build_packet_deterministic_and_valid():
    pack = build_ideation_operator_packet(
        input_mode="PROMPT_LED",
        venture_name="Test Venture",
        overlap_classification="NOVEL",
        evidence_pack={
            "status": "OBSERVED",
            "pack_ref": "pack_test_1",
            "claims": [],
            "sources": [{"source_id": "s1"}],
        },
        score_vector={"novelty": 0.5},
    )
    assert pack["schema_version"] == SCHEMA_VERSION
    assert pack["pipeline_id"] == "neon_genie_ideation"
    assert pack["authority"]["execution_authority"] is False
    assert pack["commercial_claims_blocked"] is True
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"
    h1 = pack["canonical_hash"]
    pack2 = build_ideation_operator_packet(
        input_mode="PROMPT_LED",
        venture_name="Test Venture",
        overlap_classification="NOVEL",
        evidence_pack={
            "status": "OBSERVED",
            "pack_ref": "pack_test_1",
            "claims": [],
            "sources": [{"source_id": "s1"}],
        },
        score_vector={"novelty": 0.5},
    )
    assert pack2["canonical_hash"] == h1
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(pack)


def test_duplicate_blocks_readiness():
    pack = build_ideation_operator_packet(
        overlap_classification="DUPLICATE",
        venture_name="Dup",
    )
    assert pack["readiness"] == "BLOCKED"
    assert "OVERLAP_GATE" in pack["blocked_by"]


def test_from_venture_packet():
    venture = {
        "input_mode": "MARKET_LED",
        "venture_name": "From Venture",
        "output_class": "SOFTWARE",
        "overlap_classification": "ADJACENT",
        "route_binding": "abx-familiar",
        "evidence_pack_ref": "ref_1",
        "evidence_basis": "INFERRED",
        "score_vector": {"fit": 0.2},
    }
    packet = build_ideation_operator_packet_from_venture(venture)
    assert packet["venture_name"] == "From Venture"
    assert packet["overlap_classification"] == "ADJACENT"
    assert packet["evidence_pack_ref"] == "ref_1"
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(packet)
