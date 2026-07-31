"""Tests for NoctisDreamOperatorPacket.v0 (Track B MISSING_CONTRACT closure)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.noctis.dream_operator_packet import (
    build_dream_operator_packet,
    build_dream_operator_packet_from_input,
    extract_motifs,
    normalize_dream,
)

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "noctis" / "dream_operator_packet.v0.schema.json"


def test_normalize_and_motifs_deterministic():
    n1 = normalize_dream("  forest   of  symbols  ")
    n2 = normalize_dream("forest of symbols")
    assert n1 == n2 == "forest of symbols"
    m1 = extract_motifs(n1, "dream_x")
    m2 = extract_motifs(n2, "dream_x")
    assert m1 == m2
    assert all(m["register"] == "INFERRED" for m in m1)


def test_operator_packet_from_synthetic_dream():
    pack = build_dream_operator_packet(
        mode="SYSTEM_DREAM",
        dream_id="synth_001",
        source="SYSTEM",
        privacy_tier="PUBLIC_SYNTHETIC",
        narrative_raw=(
            "I was walking through a forest of glowing symbols that kept "
            "repeating the same phrase about continuity."
        ),
        seed="test-seed-42",
    )
    assert pack["schema_version"] == "NoctisDreamOperatorPacket.v0"
    assert pack["pipeline_id"] == "noctis_dream"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"
    assert pack["medical_claims_blocked"] is True
    assert pack["forecast_routing_blocked"] is True
    assert pack["memory_direct_write_blocked"] is True
    assert pack["authority"]["medical_claims_allowed"] is False
    assert pack["authority"]["execution_authority"] is False
    assert pack["ir"]["schema_version"] == "NoctisDreamIR.v0"
    assert pack["ir"]["motif_count"] >= 1
    assert pack["narrative_excerpt_allowed"] is True
    assert "narrative_excerpt" in pack
    assert len(pack["canonical_hash"]) == 64

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(pack)


def test_private_narrative_not_in_packet():
    pack = build_dream_operator_packet(
        mode="HUMAN_DREAM",
        dream_id="priv_001",
        source="USER",
        privacy_tier="PRIVATE",
        narrative_raw="A private dream about a river of keys.",
    )
    assert pack["narrative_excerpt_allowed"] is False
    assert "narrative_excerpt" not in pack
    assert pack["narrative_present"] is True
    assert len(pack["narrative_sha256"]) == 64
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"


def test_empty_narrative_not_computable():
    pack = build_dream_operator_packet(
        mode="HUMAN_DREAM",
        narrative_raw="   ",
        privacy_tier="PRIVATE",
    )
    assert pack["readiness"] == "NOT_COMPUTABLE"
    assert "EMPTY_NARRATIVE" in pack["blocked_by"]
    assert pack["ir"]["motif_count"] == 0


def test_deterministic_hash():
    kwargs = dict(
        mode="SYSTEM_DREAM",
        dream_id="d1",
        source="SYSTEM",
        privacy_tier="PUBLIC_SYNTHETIC",
        narrative_raw="symbols in a forest of continuity",
        seed="s1",
    )
    a = build_dream_operator_packet(**kwargs)
    b = build_dream_operator_packet(**kwargs)
    assert a == b
    assert a["canonical_hash"] == b["canonical_hash"]


def test_from_input_dict():
    dream_input = {
        "schema_version": "DreamInput.v1",
        "dream_id": "synth_002",
        "source": "SYSTEM",
        "privacy_tier": "PUBLIC_SYNTHETIC",
        "narrative_raw": "repeating motifs of gates and mirrors",
        "seed": "42",
    }
    pack = build_dream_operator_packet_from_input(dream_input, mode="SYSTEM_DREAM")
    assert pack["dream_id"] == "synth_002"
    assert pack["source"] == "SYSTEM"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"


def test_runner_attaches_operator_packet(tmp_path: Path):
    """scripts/research/run_noctis_dream.py attaches core operator packet."""
    import importlib.util
    import sys

    runner = REPO / "scripts" / "research" / "run_noctis_dream.py"
    spec = importlib.util.spec_from_file_location("run_noctis_dream", runner)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_noctis_dream"] = mod
    spec.loader.exec_module(mod)

    dream_input = {
        "schema_version": "DreamInput.v1",
        "dream_id": "runner_001",
        "source": "SYSTEM",
        "privacy_tier": "PUBLIC_SYNTHETIC",
        "narrative_raw": "A forest of glowing symbols about continuity.",
        "seed": "r1",
    }
    normalized = mod.normalize_dream(dream_input["narrative_raw"])
    dream_input["narrative_normalized"] = normalized
    motifs = mod.extract_motifs(normalized, dream_input["dream_id"])
    delivery = mod.build_delivery("SYSTEM_DREAM", dream_input, motifs)
    assert "operator_packet" in delivery
    op = delivery["operator_packet"]
    assert op["schema_version"] == "NoctisDreamOperatorPacket.v0"
    assert op["readiness"] == "SHADOW_OPERATOR_REVIEW"
    assert op["ir"]["motif_count"] == len(motifs)
