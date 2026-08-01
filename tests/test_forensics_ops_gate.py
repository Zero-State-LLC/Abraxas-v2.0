# tests/test_forensics_ops_gate.py
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.forensics.ops_gate import build_memetic_ops_gate

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "contracts/forensics/memetic_ops_gate.v0.schema.json"


def test_ready_still_denied():
    gate = build_memetic_ops_gate(
        {
            "disposition": "READY",
            "canonical_hash": "a" * 64,
            "ops_gate_hint": "WOULD_ALLOW_IF_OPERATOR",
        }
    )
    assert gate["schema_version"] == "MemeticOpsGate.v0"
    assert gate["gate_status"] == "DENIED"
    assert gate["simulation"] == "WOULD_ALLOW"
    assert gate["publish_authorized"] is False
    assert gate["execution_authorized"] is False


def test_hold_denied():
    gate = build_memetic_ops_gate({"disposition": "HOLD", "canonical_hash": "b" * 64})
    assert gate["gate_status"] == "DENIED"
    assert gate["simulation"] == "WOULD_DENY"


def test_none_disposition_denied():
    gate = build_memetic_ops_gate(None)
    assert gate["schema_version"] == "MemeticOpsGate.v0"
    assert gate["gate_status"] == "DENIED"
    assert gate["simulation"] == "WOULD_DENY"
    assert gate["publish_authorized"] is False
    assert gate["execution_authorized"] is False
    assert gate["advisory_only"] is True
    assert gate["lane"] == "SHADOW"


def test_schema_validates_ready_denied():
    gate = build_memetic_ops_gate(
        {
            "disposition": "READY",
            "canonical_hash": "c" * 64,
            "ops_gate_hint": "WOULD_ALLOW_IF_OPERATOR",
        }
    )
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(gate)
