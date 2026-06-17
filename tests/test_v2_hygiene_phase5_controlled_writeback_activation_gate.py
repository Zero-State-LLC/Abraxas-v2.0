from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase5_controlled_writeback_activation_gate import (
    READY_STATUS,
    build_v2_hygiene_phase5_controlled_writeback_activation_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase5_controlled_writeback_activation_gate.v1.schema.json"
)


def test_controlled_writeback_gate_ready() -> None:
    packet = build_v2_hygiene_phase5_controlled_writeback_activation_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["controlled_writeback_activation_gate_ready"] is True
    assert packet["controlled_writeback_enabled"] is True
    assert packet["valid_for_controlled_writeback"] is True
    assert packet["recommended_next_lane"] == "V2_HYGIENE_PHASE6_EXECUTION_SURFACE_PROMOTION_GATE_001"
    assert packet["downstream"] == "NOT_COMPUTABLE"
    assert packet["dependency_denial_contract"]["package_lock_mutation_authorized"] is False
    assert packet["dependency_denial_contract"]["npmrc_stabilization_observed"] is True


def test_controlled_writeback_schema_and_hash() -> None:
    packet = build_v2_hygiene_phase5_controlled_writeback_activation_gate(REPO_ROOT)
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("controlled_writeback_activation_gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
