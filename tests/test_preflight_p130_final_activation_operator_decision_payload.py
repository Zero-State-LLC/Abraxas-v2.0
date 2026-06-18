from __future__ import annotations

import json
from pathlib import Path

from core.research_canary_final_activation_operator_decision_record import P130_PATH
from scripts.preflight_p130_final_activation_operator_decision_payload import (
    validate_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_TEMPLATE = (
    "operator_input/templates/p130_final_activation_operator_decision_payload_001.example.json"
)
REAL_PAYLOAD = "operator_input/p130_final_activation_operator_decision_payload_001.json"


def _p130_packet() -> dict:
    return json.loads((REPO_ROOT / P130_PATH).read_text(encoding="utf-8"))


def test_p130_template_passes_template_mode() -> None:
    payload = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE).read_text(encoding="utf-8"))
    assert validate_payload(payload, p130_packet=_p130_packet(), template_mode=True) == []


def test_p130_template_fails_real_mode_due_to_placeholders() -> None:
    payload = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE).read_text(encoding="utf-8"))
    blockers = validate_payload(payload, p130_packet=_p130_packet(), template_mode=False)
    assert any("placeholder" in blocker for blocker in blockers)


def test_p130_real_payload_passes_real_mode() -> None:
    payload = json.loads((REPO_ROOT / REAL_PAYLOAD).read_text(encoding="utf-8"))
    assert validate_payload(payload, p130_packet=_p130_packet(), template_mode=False) == []


def test_p130_upstream_hash_mismatch_blocked() -> None:
    payload = json.loads((REPO_ROOT / REAL_PAYLOAD).read_text(encoding="utf-8"))
    payload["upstream_acknowledgement"]["upstream_packet_hash"] = "deadbeef"
    blockers = validate_payload(payload, p130_packet=_p130_packet(), template_mode=False)
    assert "upstream_packet_hash_mismatch" in blockers
