from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.runtime_integration_gate_receipt import build_runtime_integration_gate_receipt
from scripts.runtime import run_runtime_integration_gate_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/runtime_integration_gate_receipt.v1.schema.json"


def test_runtime_integration_gate_receipt_is_advisory_only() -> None:
    packet = build_runtime_integration_gate_receipt(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "RuntimeIntegrationGateReceipt.v1"
    assert packet["receipt_status"] == "RUNTIME_INTEGRATION_GATE_RECEIPT_READY_ADVISORY_ONLY"
    assert packet["target_surface"] == "ABRAXAS_RUNTIME_INTEGRATION_GATE_001"
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_runtime_wiring"] is False
    assert packet["mandatory_pre_dispatch_gate_enabled"] is False
    assert packet["duplicate_runtime_authority_created"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["execution_authority"] is False
    assert packet["operator_command_authority"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["authority_locks"]["mandatory_pre_dispatch_gate_enabled"] is False


def test_runtime_integration_gate_receipt_covers_required_subsystems_and_fields() -> None:
    packet = build_runtime_integration_gate_receipt(repo_root=REPO_ROOT)

    assert packet["notion_gap_evidence"]["implementation_status"] == "PARTIAL"
    assert packet["covered_subsystem_count"] == 7
    assert packet["receipt_summary"]["all_subsystems_declare_required_fields"] is True
    assert packet["receipt_summary"]["ready_for_live_runtime_wiring"] is False
    required_fields = set(packet["required_declaration_fields"])
    for record in packet["covered_subsystems"]:
        assert set(record["declared_fields"]) == required_fields
        assert record["field_completeness"] == "COMPLETE"
        assert record["governance_locks"]["runtime_mutation"] is False
        assert record["no_authority_seal"]["execution_authority"] is False


def test_runtime_integration_gate_receipt_schema_and_hash_are_stable() -> None:
    packet = build_runtime_integration_gate_receipt(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runtime_integration_gate_receipt_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/runtime_integration_gate_receipt_001.latest.json"
    out_md = tmp_path / "out/audit/runtime_integration_gate_receipt_001.latest.md"

    first = run_runtime_integration_gate_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_runtime_integration_gate_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith("# Runtime Integration Gate Receipt 001\n")
