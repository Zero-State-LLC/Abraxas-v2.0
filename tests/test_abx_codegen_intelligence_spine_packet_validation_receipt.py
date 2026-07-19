from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_packet_validation_receipt import (
    EXPECTED_NEGATIVE_RULES,
    EXPECTED_VALID_FIXTURES,
    build_abx_codegen_intelligence_spine_packet_validation_receipt,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_packet_validation_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_packet_validation_receipt.v1.schema.json"
)


def test_codegen_packet_validation_receipt_is_advisory_only() -> None:
    packet = build_abx_codegen_intelligence_spine_packet_validation_receipt(
        repo_root=REPO_ROOT
    )

    assert (
        packet["artifact_type"]
        == "AbxCodegenIntelligenceSpinePacketValidationReceipt.v1"
    )
    assert (
        packet["receipt_status"]
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_PACKET_VALIDATION_RECEIPT_READY"
    )
    assert packet["target_surface"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_001"
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["schema_mutation_performed"] is False
    assert packet["fixture_mutation_performed"] is False
    assert packet["shadow_replay_execution_performed"] is False
    assert packet["operator_decision_record_created"] is False
    assert packet["meta_gate_seal_created"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_packet_validation_receipt_validates_all_expected_fixtures() -> None:
    packet = build_abx_codegen_intelligence_spine_packet_validation_receipt(
        repo_root=REPO_ROOT
    )
    records = {
        record["fixture_name"]: record for record in packet["fixture_validation_records"]
    }

    assert set(EXPECTED_VALID_FIXTURES) <= set(records)
    assert set(EXPECTED_NEGATIVE_RULES) <= set(records)
    for fixture_name in EXPECTED_VALID_FIXTURES:
        record = records[fixture_name]
        assert record["validation_status"] == "PASS"
        assert record["schema_valid"] is True
        assert record["semantic_errors"] == []
    for fixture_name, expected_rules in EXPECTED_NEGATIVE_RULES.items():
        record = records[fixture_name]
        assert record["validation_status"] == "EXPECTED_REJECTION"
        assert record["expected_negative_rules_observed"] is True
        assert set(expected_rules) <= set(record["semantic_errors"])

    summary = packet["fixture_validation_summary"]
    assert summary["valid_fixture_pass_count"] == len(EXPECTED_VALID_FIXTURES)
    assert summary["negative_fixture_expected_rejection_count"] == len(
        EXPECTED_NEGATIVE_RULES
    )
    assert summary["validation_passed"] is True
    assert summary["shadow_replay_executed"] is False
    assert summary["wall_clock_used"] is False
    assert summary["fixture_timestamps_are_source_observed"] is True


def test_codegen_packet_validation_receipt_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_packet_validation_receipt(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_packet_validation_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_packet_validation_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_packet_validation_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith(
        "# ABX Codegen Intelligence Spine Packet Validation Receipt\n"
    )
