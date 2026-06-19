from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_harness_implementation_authorization_intake_gate import (
    DEFAULT_PAYLOAD_PATH,
    build_abx_harness_implementation_authorization_intake_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_payload_observed_at_canonical_path() -> None:
    assert (REPO_ROOT / DEFAULT_PAYLOAD_PATH).is_file()


def test_intake_gate_validated_with_operator_authorization() -> None:
    packet = build_abx_harness_implementation_authorization_intake_gate(REPO_ROOT)
    assert (
        packet["status"] == "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_INTAKE_VALIDATED"
    )
    assert packet["authorization_payload_observed"] is True
    assert packet["intake_validated_for_authorization_record"] is True
    assert packet["source_gate_held_for_operator"] is True
    assert packet["operator_decision_value"] == "approve_harness_implementation_record"
    assert packet["execution_authority"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["validation_blockers"] == []


def test_intake_gate_deterministic() -> None:
    first = build_abx_harness_implementation_authorization_intake_gate(REPO_ROOT)
    second = build_abx_harness_implementation_authorization_intake_gate(REPO_ROOT)
    assert first["gate_hash"] == second["gate_hash"]
    assert first == second


def test_intake_gate_schema_validates() -> None:
    packet = build_abx_harness_implementation_authorization_intake_gate(REPO_ROOT)
    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/abx_harness_implementation_authorization_intake_gate.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
