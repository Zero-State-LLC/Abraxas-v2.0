from __future__ import annotations

import json
from pathlib import Path

from scripts.preflight.preflight_oracle_signal_physical_implementation_authorization_payload import (
    _source_review_hash,
    validate_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_TEMPLATE = (
    "operator_input/templates/oracle_signal_physical_implementation_authorization_payload_001.example.json"
)
REAL_PAYLOAD = "operator_input/oracle_signal_physical_implementation_authorization_payload_001.json"


def test_oracle_template_passes_template_mode() -> None:
    payload = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE).read_text(encoding="utf-8"))
    assert validate_payload(payload, expected_review_hash=_source_review_hash(REPO_ROOT), template_mode=True) == []


def test_oracle_template_fails_real_mode_due_to_placeholders() -> None:
    payload = json.loads((REPO_ROOT / EXAMPLE_TEMPLATE).read_text(encoding="utf-8"))
    blockers = validate_payload(
        payload,
        expected_review_hash=_source_review_hash(REPO_ROOT),
        template_mode=False,
    )
    assert any("placeholder" in blocker for blocker in blockers)


def test_oracle_real_payload_passes_real_mode() -> None:
    payload = json.loads((REPO_ROOT / REAL_PAYLOAD).read_text(encoding="utf-8"))
    assert validate_payload(
        payload,
        expected_review_hash=_source_review_hash(REPO_ROOT),
        template_mode=False,
    ) == []


def test_oracle_hash_mismatch_blocked() -> None:
    payload = json.loads((REPO_ROOT / REAL_PAYLOAD).read_text(encoding="utf-8"))
    payload["operator_decision"]["source_review_hash"] = "deadbeef"
    blockers = validate_payload(
        payload,
        expected_review_hash=_source_review_hash(REPO_ROOT),
        template_mode=False,
    )
    assert "source_review_hash_mismatch" in blockers
