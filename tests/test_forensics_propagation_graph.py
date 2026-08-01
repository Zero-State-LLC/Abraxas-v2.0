# tests/test_forensics_propagation_graph.py
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft7Validator
from core.forensics.propagation_graph import build_propagation_graph_from_pack

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
SCHEMA = REPO / "contracts/forensics/propagation_graph.v0.schema.json"


def test_graph_from_fixture_deterministic():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    a = build_propagation_graph_from_pack(pack)
    b = build_propagation_graph_from_pack(pack)
    assert a == b
    assert a["schema_version"] == "PropagationGraph.v0"
    assert a["write_performed"] is False
    assert a["network_calls"] is False
    assert len(a["nodes"]) >= 1
    assert a["authority"]["execution_authority"] is False
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(a)


def test_graph_none_pack():
    g = build_propagation_graph_from_pack(None)
    assert g["schema_version"] == "PropagationGraph.v0"
    assert g["nodes"] == []
    assert g["edges"] == []
