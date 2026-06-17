from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt import (
    NEXT_OPERATOR_GATE_LANE,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt,
    render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt,
)
from scripts import (
    run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "execution_receipt.v1.schema.json"
)
SOURCE_IMPLEMENTATION_RECEIPT_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "implementation_receipt_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_completion_validation_execution_receipt_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT
    )

    assert first["execution_receipt_hash"] == second["execution_receipt_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["execution_receipt_ready"] is True
    assert first["completion_validation_claim_evaluation_performed"] is True
    assert first["recommended_next_lane"] == NEXT_OPERATOR_GATE_LANE
    assert first["downstream"] == "NOT_COMPUTABLE"
    assert first["valid_for_decision_record_completion_validation"] is False
    assert first["valid_for_writeback"] is False
    assert first["valid_for_execution"] is False
    assert first["safe_to_auto_continue"] is False


def test_completion_validation_execution_receipt_missing_source_fails_closed(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT,
        source_completion_validation_implementation_receipt_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "EXECUTION_RECEIPT_BLOCKED"
    )
    assert packet["execution_receipt_ready"] is False
    assert "required_completion_validation_implementation_receipt_missing" in packet[
        "source_blockers"
    ]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["decision_record_completion_validation_performed"] is False


def test_completion_validation_execution_receipt_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    implementation_receipt = _read_json(SOURCE_IMPLEMENTATION_RECEIPT_PATH)
    implementation_receipt["decision_record_completion_validation_performed"] = True
    implementation_receipt["authority_locks"]["decision_record_completion_validation"] = True
    source = _write_source(tmp_path, "authorizing_implementation_receipt.json", implementation_receipt)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT,
        source_completion_validation_implementation_receipt_path=source,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "EXECUTION_RECEIPT_BLOCKED"
    )
    assert (
        "implementation_receipt_authority_expanding_field:"
        "decision_record_completion_validation_performed"
    ) in packet["source_blockers"]
    assert (
        "implementation_receipt_authority_lock_true:"
        "decision_record_completion_validation"
    ) in packet["source_blockers"]
    assert packet["execution_receipt_ready"] is False
    assert packet["decision_record_completion_validation_authorized"] is False
    assert packet["decision_record_completion_validation_performed"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_completion_validation_execution_receipt_claim_failure_blocks(
    tmp_path: Path,
) -> None:
    implementation_receipt = _read_json(SOURCE_IMPLEMENTATION_RECEIPT_PATH)
    implementation_receipt["validation_packet_contract"]["validation_claims"][0][
        "claim_validated"
    ] = False
    source = _write_source(tmp_path, "claim_failed_implementation_receipt.json", implementation_receipt)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT,
        source_completion_validation_implementation_receipt_path=source,
    )

    claims = packet["execution_packet"]["executed_validation_claims"]
    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "EXECUTION_RECEIPT_BLOCKED"
    )
    assert "implementation_receipt_validation_claims_not_all_true" in packet[
        "source_blockers"
    ]
    assert claims[0]["execution_status"] == "BLOCKED"
    assert claims[0]["fail_closed_blocker"] == "claim_not_validated:source_approval_gate_ready"


def test_completion_validation_execution_receipt_contracts_are_non_authoritative() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT
    )
    execution_packet = packet["execution_packet"]
    brier_contract = packet["brier_scoring_contract"]
    rune_mapping = packet["rune_governance_mapping"]

    assert execution_packet["claim_evaluation_performed"] is True
    assert execution_packet["completion_validation_authorized"] is False
    assert execution_packet["completion_validation_performed"] is False
    assert execution_packet["execution_receipt_only"] is True
    assert all(value is False for value in execution_packet["authority_denials"].values())
    assert execution_packet["claim_evaluation_count"] == execution_packet[
        "claims_validated_count"
    ]
    assert all(
        claim["execution_status"] == "CLAIM_VALIDATED"
        for claim in execution_packet["executed_validation_claims"]
    )
    assert all(
        claim["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
        for claim in execution_packet["executed_validation_claims"]
    )
    assert brier_contract["telemetry_only"] is True
    assert brier_contract["brier_score_formula"] == (
        "(forecast_probability - binary_outcome)^2"
    )
    assert brier_contract["resolution_allowed"] is False
    assert brier_contract["adaptive_learning_authorized"] is False
    assert brier_contract["forecast_routing_authorized"] is False
    assert brier_contract["promotion_authorized"] is False
    assert all(hook["resolution_allowed"] is False for hook in brier_contract["telemetry_hooks"])
    assert {item["rune"] for item in rune_mapping} == {
        "Observe",
        "Bind",
        "Hold",
        "Weigh",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in rune_mapping)


def test_completion_validation_execution_receipt_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["decision_record_creation_authorized"] is False
    assert packet["decision_record_completed"] is False
    assert packet["decision_record_completion_authorized"] is False
    assert packet["decision_record_completion_validation_authorized"] is False
    assert packet["decision_record_completion_validation_performed"] is False
    assert packet["decision_record_emitted"] is False
    assert packet["decision_record_emission_authorized"] is False
    assert packet["decision_record_finalized"] is False
    assert packet["decision_record_finalization_authorized"] is False
    assert packet["decision_record_materialized"] is False
    assert packet["decision_record_materialization_authorized"] is False
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


def test_completion_validation_execution_receipt_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("execution_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_completion_validation_execution_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["execution_receipt_hash"] == packet["execution_receipt_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_completion_validation_execution_receipt_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion "
        "Validation Execution Receipt"
    )
    assert any("## Execution Packet" in line for line in markdown)
    assert any("telemetry_only: True" in line for line in markdown)
    assert any("forecast_routing_authorized: False" in line for line in markdown)
