from __future__ import annotations

import json
from pathlib import Path

from scripts.preflight.preflight_daniel_meyer_operator_hold_clearance_attestation import (
    validate_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_TEMPLATE = (
    "operator_input/templates/daniel_meyer_operator_hold_clearance_attestation_001.example.json"
)
REAL_PAYLOAD = "operator_input/daniel_meyer_operator_hold_clearance_attestation_001.json"


def test_master_template_passes_template_mode() -> None:
    payload = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE).read_text(encoding="utf-8"))
    assert validate_payload(payload, template_mode=True) == []


def test_master_template_fails_real_mode_due_to_placeholders() -> None:
    payload = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE).read_text(encoding="utf-8"))
    blockers = validate_payload(payload, template_mode=False)
    assert any("placeholder" in blocker for blocker in blockers)


def test_master_real_payload_passes_real_mode() -> None:
    payload = json.loads((REPO_ROOT / REAL_PAYLOAD).read_text(encoding="utf-8"))
    assert validate_payload(payload, template_mode=False) == []
