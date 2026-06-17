from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt import (
    READY_STATUS,
    build_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt.v1.schema.json"
)


def test_root_cause_receipt_ready() -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt(
        REPO_ROOT
    )

    assert packet["status"] == READY_STATUS
    assert packet["root_cause_receipt_ready"] is True
    assert packet["recommended_next_lane"] == "V2_HYGIENE_PHASE5_CONTROLLED_WRITEBACK_ACTIVATION_GATE_001"
    assert packet["downstream"] == "NOT_COMPUTABLE"
    assert packet["root_cause_analysis_contract"]["root_cause_sealed"] is True
    assert packet["dependency_mutation_authorized"] is False


def test_root_cause_schema_and_hash() -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("root_cause_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
