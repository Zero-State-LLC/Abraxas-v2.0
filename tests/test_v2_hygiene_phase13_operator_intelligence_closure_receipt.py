from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase13_operator_intelligence_closure_receipt import (
    EXPECTED_ENTRY_HASH,
    NOT_COMPUTABLE,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase13_operator_intelligence_closure_receipt,
    write_v2_hygiene_phase13_operator_intelligence_closure_receipt,
)
from scripts import run_v2_hygiene_phase13_operator_intelligence_closure_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase13_operator_intelligence_closure_receipt.v1.schema.json"
)
SOURCE_ENTRY_PATH = (
    "out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_closure_receipt_ready() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_closure_receipt(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_intelligence_closure_receipt_ready"] is True
    assert packet["phase13_entry_receipt_hash_verified"] is True
    assert packet["source_blockers"] == []
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["downstream"] == "NOT_COMPUTABLE"
    assert packet["brier_resolution_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["phase14_activation_authorized"] is False


def test_hash_chain_pins_phase12_and_entry() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_closure_receipt(REPO_ROOT)
    chain = packet["hash_chain_contract"]

    assert chain["phase12_gate_hash"] == (
        "584a23af8e8ea22e0971a380ef35dc8b835e45bc5f1e1c8c996c508d92e36e9c"
    )
    assert chain["phase13_entry_receipt_hash"] == EXPECTED_ENTRY_HASH
    assert chain["hash_chain_verified"] is True
    assert packet["operator_intelligence_closure_receipt_hash"] != NOT_COMPUTABLE


def test_deliverable_inventory_complete() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_closure_receipt(REPO_ROOT)
    inventory = packet["deliverable_inventory_contract"]

    assert inventory["all_observed"] is True
    assert all(item["observed"] for item in inventory["deliverables"])


def test_status_atlas_and_claims() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_closure_receipt(REPO_ROOT)
    atlas = packet["status_atlas"]

    assert atlas["phase"] == 13
    assert atlas["operator_review_posture"] == "ACTIVE"
    assert atlas["phase13_tests_passed"] is True
    assert atlas["surfaces"]["notion_sync_hook"]["writeback"] is False
    assert {claim["classification"] for claim in packet["closure_claims"]} <= {
        "OBSERVED",
        "INFERRED",
        "SPECULATIVE",
    }


def test_missing_entry_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_closure_receipt(
        REPO_ROOT,
        source_entry_receipt_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_CLOSURE_RECEIPT_BLOCKED"
    )
    assert "required_phase13_entry_receipt_missing" in packet["source_blockers"]


def test_entry_hash_mutation_fails_closed(tmp_path: Path) -> None:
    entry = _read_json(SOURCE_ENTRY_PATH)
    entry["operator_intelligence_entry_receipt_ready"] = False
    source = _write_source(tmp_path, "mutated_entry.json", entry)

    packet = build_v2_hygiene_phase13_operator_intelligence_closure_receipt(
        REPO_ROOT,
        source_entry_receipt_path=source,
    )

    assert packet["operator_intelligence_closure_receipt_ready"] is False
    assert "phase13_entry_receipt_self_hash_mismatch" in packet["source_blockers"]


def test_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_closure_receipt(REPO_ROOT)
    packet_without_hash = dict(packet)
    closure_hash = packet_without_hash.pop("operator_intelligence_closure_receipt_hash")
    assert closure_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase13_operator_intelligence_closure_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase13_operator_intelligence_closure_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["operator_intelligence_closure_receipt_hash"] == packet[
        "operator_intelligence_closure_receipt_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
