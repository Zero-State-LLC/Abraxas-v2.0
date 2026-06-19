from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_harness_implementation_authorization_record import (
    build_abx_harness_implementation_authorization_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_authorization_record_emitted_for_operator_approval() -> None:
    packet = build_abx_harness_implementation_authorization_record(REPO_ROOT)
    assert (
        packet["status"] == "ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_RECORD_EMITTED"
    )
    assert packet["implementation_authorized"] is True
    assert packet["implementation_may_proceed"] is True
    assert packet["safe_to_prepare_implementation_pr"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["authorization_class"] == "IMPLEMENTATION_APPROVED_RECORD_ONLY"
    assert packet["execution_status"] == "NOT_AUTHORIZED_FOR_EXECUTION"


def test_authorization_record_preserves_authority_locks() -> None:
    packet = build_abx_harness_implementation_authorization_record(REPO_ROOT)
    locks = packet["authority_locks"]
    assert locks["implementation_authority"] is True
    assert locks["execution_authority"] is False
    assert locks["runtime_execution"] is False
    assert locks["canon_promotion"] is False


def test_authorization_record_deterministic() -> None:
    first = build_abx_harness_implementation_authorization_record(REPO_ROOT)
    second = build_abx_harness_implementation_authorization_record(REPO_ROOT)
    assert first["record_hash"] == second["record_hash"]
    assert first == second


def test_authorization_record_schema_validates() -> None:
    packet = build_abx_harness_implementation_authorization_record(REPO_ROOT)
    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/abx_harness_implementation_authorization_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
