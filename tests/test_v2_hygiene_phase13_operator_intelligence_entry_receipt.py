from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase13_operator_intelligence_entry_receipt import (
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase13_operator_intelligence_entry_receipt,
    render_v2_hygiene_phase13_operator_intelligence_entry_receipt_markdown,
    write_v2_hygiene_phase13_operator_intelligence_entry_receipt,
)
from scripts.hygiene import run_v2_hygiene_phase13_operator_intelligence_entry_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase13_operator_intelligence_entry_receipt.v1.schema.json"
)
SOURCE_PHASE12_PATH = (
    "out/operator_review/v2_hygiene_phase6_execution_surface_promotion_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_operator_intelligence_entry_receipt_ready() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert packet["source_blockers"] == []
    assert packet["operator_intelligence_entry_receipt_ready"] is True
    assert packet["phase12_execution_surface_promotion_gate_hash_verified"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["downstream"] == "NOT_COMPUTABLE"
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["valid_for_controlled_writeback"] is True
    assert packet["valid_for_execution"] is False


def test_phase_transition_contract_fields() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(REPO_ROOT)
    transition = packet["phase_transition_receipt_contract"]

    assert transition["phase"] == 13
    assert transition["authority_state"] == "read/controlled-write"
    assert transition["operator_review_posture"] == "ACTIVE"
    assert transition["timestamp_utc"] == "NOT_COMPUTABLE"
    assert transition["spine_hash"] != "NOT_COMPUTABLE"
    assert len(transition["claims"]) >= 4
    assert all(
        claim["classification"] in {"OBSERVED", "INFERRED", "SPECULATIVE"}
        for claim in transition["claims"]
    )


def test_mcp_integration_contract_observed() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(REPO_ROOT)
    mcp = packet["mcp_integration_contract"]

    assert mcp["mcp_json_example_observed"] is True
    assert mcp["mcp_rules_observed"] is True
    assert mcp["mcp_auto_writeback_authorized"] is False
    assert mcp["operator_local_install_required"] is True


def test_brier_and_rune_contracts_are_non_authoritative() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(REPO_ROOT)
    brier = packet["brier_scoring_contract"]
    runes = packet["rune_governance_mapping"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    assert all(hook["resolution_allowed"] is False for hook in brier["telemetry_hooks"])
    assert {item["rune"] for item in runes} == {"Observe", "Bind", "Hold", "Weigh", "Seal"}
    assert all(item["authority_granted"] is False for item in runes)
    assert packet["rune_registration_authorized"] is False
    assert packet["mcp_auto_writeback_authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_missing_phase12_source_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(
        REPO_ROOT,
        source_phase12_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_ENTRY_RECEIPT_BLOCKED"
    assert packet["operator_intelligence_entry_receipt_ready"] is False
    assert "required_phase12_execution_surface_promotion_gate_missing" in packet[
        "source_blockers"
    ]
    assert packet["phase12_execution_surface_promotion_gate_hash_verified"] is False


def test_phase12_authority_mutation_fails_closed(tmp_path: Path) -> None:
    phase12 = _read_json(SOURCE_PHASE12_PATH)
    phase12["execution_surface_promotion_authorized"] = True
    source = _write_source(tmp_path, "mutated_phase12.json", phase12)

    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(
        REPO_ROOT,
        source_phase12_gate_path=source,
    )

    assert packet["operator_intelligence_entry_receipt_ready"] is False
    assert (
        "phase12_execution_surface_promotion_gate_authority_expanding_field:"
        "execution_surface_promotion_authorized"
    ) in packet["source_blockers"]


def test_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(REPO_ROOT)
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("operator_intelligence_entry_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase13_operator_intelligence_entry_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase13_operator_intelligence_entry_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["operator_intelligence_entry_receipt_hash"] == packet[
        "operator_intelligence_entry_receipt_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_markdown() -> None:
    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(REPO_ROOT)
    markdown = render_v2_hygiene_phase13_operator_intelligence_entry_receipt_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Phase 13 Operator Intelligence Entry Receipt"
    assert any("## Phase Transition Contract" in line for line in markdown)
    assert any("## MCP Integration Contract" in line for line in markdown)
    assert any("brier_resolution_authorized: False" in line for line in markdown)
