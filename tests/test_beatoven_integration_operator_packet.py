"""Tests for BeatOvenPsyFiIntegrationOperatorPacket.v0 (Notion PATCH-006)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.beatoven.integration_operator_packet import (
    SHARED_RUNES,
    build_integration_operator_packet,
    build_integration_operator_packet_from_intent,
    derive_sonic_plan,
)

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts" / "beatoven" / "integration_operator_packet.v0.schema.json"


def test_operator_packet_schema_and_locks():
    pack = build_integration_operator_packet(
        intent_id="int_001",
        source_system="noctis",
        intent_summary="motif forest into pulse field",
        tempo_range_bpm=(80, 120),
        energy_level=0.6,
        density_level=0.5,
        tension_level=0.4,
        resolution_level=0.5,
        symbolic_depth_bonus=0.3,
        felt_alignment=0.7,
    )
    assert pack["schema_version"] == "BeatOvenPsyFiIntegrationOperatorPacket.v0"
    assert pack["pipeline_id"] == "beatoven_psyfi_integration"
    assert pack["lane"] == "SHADOW_ARTIFACT"
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"
    assert pack["authority"]["sonic_plan_only"] is True
    assert pack["authority"]["external_audio_render_allowed"] is False
    assert pack["authority"]["daw_control_allowed"] is False
    assert pack["authority"]["minting_allowed"] is False
    assert pack["external_audio_render_blocked"] is True
    assert pack["runic_core"]["shared"] is True
    assert "RUNE.BEATOVEN.PSYFI.BRIDGE" in pack["runic_core"]["runes"]
    assert "RUNE.PSYFI.BEATOVEN.BRIDGE" in pack["runic_core"]["runes"]
    assert pack["psyfi_bridge"]["bridge_status"] == "BRIDGED"
    assert pack["psyfi_bridge"]["subjective_feedback_only"] is True
    assert 40 <= pack["sonic_plan"]["tempo_bpm"] <= 220

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(pack)


def test_shared_runes_count():
    assert len(SHARED_RUNES) >= 10
    assert all(r.startswith("RUNE.") for r in SHARED_RUNES)


def test_sonic_plan_formulas_deterministic():
    a = derive_sonic_plan(
        tempo_range_bpm=(100, 100),
        energy_level=0.5,
        density_level=0.5,
        tension_level=0.5,
        resolution_level=0.5,
    )
    b = derive_sonic_plan(
        tempo_range_bpm=(100, 100),
        energy_level=0.5,
        density_level=0.5,
        tension_level=0.5,
        resolution_level=0.5,
    )
    assert a == b
    # mean tempo 100 + energy*18 - tension*8 = 100 + 9 - 4 = 105
    assert a["tempo_bpm"] == 105
    assert "clock" in a["graph_node_types"]
    assert "rhythm" in a["graph_node_types"]


def test_conditional_nodes():
    plan = derive_sonic_plan(
        energy_level=0.2,
        density_level=0.2,
        tension_level=0.8,
        resolution_level=0.1,
        symbolic_depth_bonus=0.0,
    )
    # high tension → transition; high grain → texture possible
    assert "transition" in plan["graph_node_types"]


def test_empty_intent_not_computable_when_unknown():
    pack = build_integration_operator_packet(
        intent_id="x",
        source_system="unknown",
        intent_summary="",
    )
    assert pack["readiness"] == "NOT_COMPUTABLE"
    assert "EMPTY_INTENT_SUMMARY" in pack["blocked_by"]


def test_from_intent_dict():
    intent = {
        "intent_id": "si_1",
        "source": {"source_system": "psyfi"},
        "intent": {
            "intent_summary": "calm resolution field",
            "tempo_range_bpm": [70, 90],
            "energy_level": 0.3,
            "density_level": 0.2,
            "tension_level": 0.2,
            "resolution_level": 0.8,
        },
        "feedback": {"felt_alignment": 0.85},
    }
    pack = build_integration_operator_packet_from_intent(intent)
    assert pack["intent_id"] == "si_1"
    assert pack["source_system"] == "psyfi"
    assert pack["psyfi_bridge"]["felt_alignment"] == 0.85
    assert pack["readiness"] == "SHADOW_OPERATOR_REVIEW"


def test_deterministic_packet():
    kwargs = dict(
        intent_id="det",
        source_system="manual",
        intent_summary="pulse",
        energy_level=0.4,
        density_level=0.4,
        tension_level=0.4,
        resolution_level=0.4,
    )
    assert build_integration_operator_packet(
        **kwargs
    ) == build_integration_operator_packet(**kwargs)
