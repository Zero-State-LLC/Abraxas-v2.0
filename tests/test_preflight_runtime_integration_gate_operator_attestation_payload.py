from __future__ import annotations

import json
from pathlib import Path

from scripts.preflight_runtime_integration_gate_operator_attestation_payload import (
    validate_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_TEMPLATE = (
    "operator_input/templates/runtime_integration_gate_operator_attestation_payload_001.example.json"
)
REAL_PAYLOAD = "operator_input/runtime_integration_gate_operator_attestation_payload_001.json"


def test_runtime_gate_template_passes_template_mode() -> None:
    payload = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE).read_text(encoding="utf-8"))
    assert validate_payload(payload, template_mode=True) == []


def test_runtime_gate_template_fails_real_mode_due_to_placeholders() -> None:
    payload = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE).read_text(encoding="utf-8"))
    blockers = validate_payload(payload, template_mode=False)
    assert any("placeholder" in blocker for blocker in blockers)


def test_runtime_gate_real_payload_passes_real_mode() -> None:
    payload = json.loads((REPO_ROOT / REAL_PAYLOAD).read_text(encoding="utf-8"))
    assert validate_payload(payload, template_mode=False) == []


def test_runtime_gate_invalid_decision_blocked() -> None:
    payload = json.loads((REPO_ROOT / REAL_PAYLOAD).read_text(encoding="utf-8"))
    payload["operator_disposition"]["selected_decision"] = "INVALID_DECISION"
    assert "selected_decision_invalid" in validate_payload(payload, template_mode=False)
