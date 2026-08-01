# tests/test_forensics_disposition.py
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft7Validator
from core.forensics.propagation_graph import build_propagation_graph_from_pack
from core.forensics.disposition import build_forensic_disposition

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
SCHEMA = REPO / "contracts/forensics/forensic_disposition.v0.schema.json"


def test_none_pack_not_computable():
    d = build_forensic_disposition(pack=None, propagation=None)
    assert d["disposition"] == "NOT_COMPUTABLE"
    assert d["ops_gate_hint"] == "DENIED"
    assert d["authority"]["publish_authorized"] is False


def test_fixture_with_propagation_ready_or_hold():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    prop = build_propagation_graph_from_pack(pack)
    d = build_forensic_disposition(pack=pack, propagation=prop, bridge_status="BRIDGED_SHADOW")
    assert d["schema_version"] == "ForensicDispositionPacket.v0"
    # C′ seal: fixture + dry-run graph must compute READY (not soft HOLD)
    assert d["disposition"] == "READY"
    assert d["ops_gate_hint"] == "WOULD_ALLOW_IF_OPERATOR"
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(d)


def test_missing_propagation_holds():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    d = build_forensic_disposition(pack=pack, propagation=None)
    assert d["disposition"] == "HOLD"
    assert "PROPAGATION_REQUIRED" in d["blocked_by"]


def test_authority_leak_holds():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    prop = build_propagation_graph_from_pack(pack)
    d = build_forensic_disposition(
        pack=pack,
        propagation=prop,
        extra_authority_violations=["authority.execution_authority"],
    )
    assert d["disposition"] == "HOLD"
    assert d["authority_violations"]
