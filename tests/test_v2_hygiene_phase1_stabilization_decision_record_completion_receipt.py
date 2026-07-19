from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_receipt import (
    NEXT_WRITEBACK_AUTHORIZATION_LANE,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt,
    render_v2_hygiene_phase1_stabilization_decision_record_completion_receipt_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_completion_receipt,
)
from scripts.hygiene import run_v2_hygiene_phase1_stabilization_decision_record_completion_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_receipt.v1.schema.json"
)
SOURCE_OPERATOR_REVIEW_GATE_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "operator_review_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_decision_record_completion_receipt_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT
    )

    assert first["completion_receipt_hash"] == second["completion_receipt_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["completion_receipt_ready"] is True
    assert first["decision_record_completed"] is True
    assert first["decision_record_completion_authorized"] is True
    assert first["decision_record_completion_receipt_emitted"] is True
    assert first["valid_for_decision_record_completion"] is True
    assert first["recommended_next_lane"] == NEXT_WRITEBACK_AUTHORIZATION_LANE
    assert first["downstream"] == "NOT_COMPUTABLE"
    assert first["valid_for_writeback"] is False
    assert first["valid_for_execution"] is False
    assert first["safe_to_auto_continue"] is False


def test_decision_record_completion_receipt_missing_source_fails_closed(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT,
        source_completion_validation_operator_review_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_RECEIPT_BLOCKED"
    )
    assert packet["completion_receipt_ready"] is False
    assert "required_completion_validation_operator_review_gate_missing" in packet[
        "source_blockers"
    ]
    assert packet["decision_record_completed"] is False
    assert packet["decision_record_completion_authorized"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_decision_record_completion_receipt_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    gate = _read_json(SOURCE_OPERATOR_REVIEW_GATE_PATH)
    gate["notion_writeback_allowed"] = True
    gate["authority_locks"]["notion_writeback"] = True
    source = _write_source(tmp_path, "authorizing_gate.json", gate)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT,
        source_completion_validation_operator_review_gate_path=source,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_RECEIPT_BLOCKED"
    )
    assert "operator_review_gate_self_hash_mismatch" in packet["source_blockers"]
    assert (
        "operator_review_gate_authority_expanding_field:notion_writeback_allowed"
        in packet["source_blockers"]
    )
    assert (
        "operator_review_gate_authority_lock_true:notion_writeback"
        in packet["source_blockers"]
    )
    assert packet["completion_receipt_ready"] is False
    assert packet["decision_record_completed"] is False
    assert packet["notion_writeback_allowed"] is False


def test_decision_record_completion_receipt_disposition_failure_blocks(
    tmp_path: Path,
) -> None:
    gate = _read_json(SOURCE_OPERATOR_REVIEW_GATE_PATH)
    gate["operator_disposition_contract"]["recommended_operator_decision"] = (
        "HOLD_FOR_OPERATOR_REVIEW"
    )
    source = _write_source(tmp_path, "held_gate.json", gate)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT,
        source_completion_validation_operator_review_gate_path=source,
    )

    assert "operator_review_gate_self_hash_mismatch" in packet["source_blockers"]
    assert "operator_disposition_not_authorizing_completion_receipt" in packet[
        "source_blockers"
    ]
    assert packet["completion_receipt_ready"] is False
    assert packet["decision_record_completed"] is False


def test_decision_record_completion_receipt_contract_shape() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT
    )
    contract = packet["decision_record_completion_contract"]
    brier_contract = packet["brier_scoring_contract"]
    rune_mapping = packet["rune_governance_mapping"]

    assert contract["record_id"] == "v2_hygiene_phase1_stabilization_decision_record_001"
    assert contract["record_output_path"] == (
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_001.latest.json"
    )
    assert contract["completion_receipt_authorized"] is True
    assert contract["completion_receipt_emitted"] is True
    assert contract["decision_record_completed"] is True
    assert contract["completion_claim_count"] == 5
    assert contract["completion_claims_finalized_count"] == 5
    assert all(
        claim["completion_status"] == "COMPLETION_CLAIM_FINALIZED"
        for claim in contract["completion_claims"]
    )
    assert all(
        claim["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
        for claim in contract["completion_claims"]
    )
    assert all(value is False for value in contract["authority_denials"].values())
    assert brier_contract["telemetry_only"] is True
    assert brier_contract["resolution_allowed"] is False
    assert brier_contract["promotion_authorized"] is False
    assert brier_contract["brier_resolution_authorized"] is False
    assert all(hook["binary_outcome"] == "NOT_COMPUTABLE" for hook in brier_contract["telemetry_hooks"])
    assert {item["rune"] for item in rune_mapping} == {
        "Observe",
        "Bind",
        "Hold",
        "Weigh",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in rune_mapping)


def test_decision_record_completion_receipt_preserves_non_completion_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT
    )

    assert packet["decision_record_completed"] is True
    assert packet["decision_record_completion_authorized"] is True
    assert packet["decision_record_created"] is False
    assert packet["decision_record_completion_validation_performed"] is False
    assert packet["decision_record_emitted"] is False
    assert packet["decision_record_finalized"] is False
    assert packet["decision_record_materialized"] is False
    assert packet["authorization_record_created"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["implementation_authorized"] is False
    assert packet["package_lock_mutation_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["runtime_mutation"] is False
    assert packet["canon_mutation"] is False
    assert packet["forecast_routing_authorized"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["promotion_authorized"] is False
    assert packet["brier_resolution_authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_decision_record_completion_receipt_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("completion_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_decision_record_completion_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_completion_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["completion_receipt_hash"] == packet["completion_receipt_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_decision_record_completion_receipt_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_decision_record_completion_receipt_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Receipt"
    )
    assert any("## Completion Contract" in line for line in markdown)
    assert any("completion_receipt_emitted: True" in line for line in markdown)
    assert any("brier_resolution_authorized: False" in line for line in markdown)
