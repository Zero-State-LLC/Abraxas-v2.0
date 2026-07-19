from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate import (
    NEXT_DECISION_RECORD_COMPLETION_RECEIPT_LANE,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate,
    render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate,
)
from scripts.hygiene import (
    run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "operator_review_gate.v1.schema.json"
)
SOURCE_EXECUTION_RECEIPT_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "execution_receipt_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_completion_validation_operator_review_gate_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT
    )

    assert first["operator_review_gate_hash"] == second["operator_review_gate_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["operator_review_gate_ready"] is True
    assert first["phase3_execution_receipt_hash_verified"] is True
    assert first["phase3_claims_validated"] is True
    assert first["recommended_next_lane"] == NEXT_DECISION_RECORD_COMPLETION_RECEIPT_LANE
    assert first["downstream"] == "NOT_COMPUTABLE"
    assert first["valid_for_decision_record_completion"] is False
    assert first["valid_for_writeback"] is False
    assert first["valid_for_execution"] is False
    assert first["safe_to_auto_continue"] is False


def test_completion_validation_operator_review_gate_missing_source_fails_closed(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT,
        source_completion_validation_execution_receipt_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "OPERATOR_REVIEW_GATE_BLOCKED"
    )
    assert packet["operator_review_gate_ready"] is False
    assert "required_completion_validation_execution_receipt_missing" in packet[
        "source_blockers"
    ]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["decision_record_completion_authorized"] is False


def test_completion_validation_operator_review_gate_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    execution_receipt = _read_json(SOURCE_EXECUTION_RECEIPT_PATH)
    execution_receipt["decision_record_completed"] = True
    execution_receipt["authority_locks"]["decision_record_completion"] = True
    source = _write_source(tmp_path, "authorizing_execution_receipt.json", execution_receipt)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT,
        source_completion_validation_execution_receipt_path=source,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "OPERATOR_REVIEW_GATE_BLOCKED"
    )
    assert "execution_receipt_self_hash_mismatch" in packet["source_blockers"]
    assert (
        "execution_receipt_authority_expanding_field:decision_record_completed"
        in packet["source_blockers"]
    )
    assert (
        "execution_receipt_authority_lock_true:decision_record_completion"
        in packet["source_blockers"]
    )
    assert packet["operator_review_gate_ready"] is False
    assert packet["decision_record_completion_authorized"] is False
    assert packet["decision_record_completed"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_completion_validation_operator_review_gate_claim_failure_blocks(
    tmp_path: Path,
) -> None:
    execution_receipt = _read_json(SOURCE_EXECUTION_RECEIPT_PATH)
    claim = execution_receipt["execution_packet"]["executed_validation_claims"][0]
    claim["claim_validated"] = False
    claim["execution_status"] = "BLOCKED"
    source = _write_source(tmp_path, "claim_failed_execution_receipt.json", execution_receipt)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT,
        source_completion_validation_execution_receipt_path=source,
    )

    assert "execution_receipt_self_hash_mismatch" in packet["source_blockers"]
    assert (
        "execution_packet_claim_not_validated:source_approval_gate_ready"
        in packet["source_blockers"]
    )
    assert (
        "execution_packet_claim_status_not_validated:source_approval_gate_ready"
        in packet["source_blockers"]
    )
    assert packet["operator_review_gate_ready"] is False


def test_completion_validation_operator_review_gate_contracts_are_non_authoritative() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT
    )
    disposition = packet["operator_disposition_contract"]
    brier_contract = packet["brier_scoring_contract"]
    rune_mapping = packet["rune_governance_mapping"]

    assert disposition["operator_decision_required"] is True
    assert disposition["recommended_operator_decision"] == (
        "AUTHORIZE_SEPARATE_DECISION_RECORD_COMPLETION_RECEIPT"
    )
    assert disposition["authorized_future_lane"] == NEXT_DECISION_RECORD_COMPLETION_RECEIPT_LANE
    assert disposition["future_lane_authorization_only"] is True
    assert disposition["decision_record_completion_performed"] is False
    assert disposition["writeback_performed"] is False
    assert disposition["package_lock_mutation_performed"] is False
    assert all(value is False for value in disposition["authority_denials"].values())
    assert brier_contract["telemetry_only"] is True
    assert brier_contract["telemetry_hooks_observed_count"] == 5
    assert brier_contract["resolution_allowed"] is False
    assert brier_contract["adaptive_learning_authorized"] is False
    assert brier_contract["forecast_routing_authorized"] is False
    assert brier_contract["promotion_authorized"] is False
    assert brier_contract["brier_resolution_authorized"] is False
    assert {item["rune"] for item in rune_mapping} == {
        "Observe",
        "Bind",
        "Hold",
        "Weigh",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in rune_mapping)


def test_completion_validation_operator_review_gate_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["decision_record_completed"] is False
    assert packet["decision_record_completion_authorized"] is False
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


def test_completion_validation_operator_review_gate_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("operator_review_gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_completion_validation_operator_review_gate_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["operator_review_gate_hash"] == packet["operator_review_gate_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_completion_validation_operator_review_gate_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion "
        "Validation Operator Review Gate"
    )
    assert any("## Operator Disposition Contract" in line for line in markdown)
    assert any("future_lane_authorization_only: True" in line for line in markdown)
    assert any("brier_resolution_authorized: False" in line for line in markdown)
