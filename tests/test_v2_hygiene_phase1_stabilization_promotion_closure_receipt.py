from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_promotion_closure_receipt import (
    NEXT_PROMOTION_AUTHORIZATION_GATE,
    NEXT_WRITEBACK_AUTHORIZATION_LANE,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase1_stabilization_promotion_closure_receipt,
    render_v2_hygiene_phase1_stabilization_promotion_closure_receipt_markdown,
    write_v2_hygiene_phase1_stabilization_promotion_closure_receipt,
)
from scripts import run_v2_hygiene_phase1_stabilization_promotion_closure_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_promotion_closure_receipt.v1.schema.json"
)
SOURCE_COMPLETION_RECEIPT_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_promotion_closure_receipt_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(REPO_ROOT)
    second = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(REPO_ROOT)

    assert first["closure_receipt_hash"] == second["closure_receipt_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["closure_receipt_ready"] is True
    assert first["phase1_stabilization_advisory_complete"] is True
    assert first["promotion_readiness_classification"] == (
        "ADVISORY_COMPLETE_NOT_CANON_PROMOTED"
    )
    assert first["recommended_next_lane"] == NEXT_WRITEBACK_AUTHORIZATION_LANE
    assert first["alternative_next_lane"] == NEXT_PROMOTION_AUTHORIZATION_GATE
    assert first["downstream"] == "NOT_COMPUTABLE"
    assert first["valid_for_writeback"] is False
    assert first["valid_for_promotion"] is False
    assert first["valid_for_activation"] is False
    assert first["valid_for_execution"] is False
    assert first["safe_to_auto_continue"] is False


def test_promotion_closure_receipt_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(
        REPO_ROOT,
        source_decision_record_completion_receipt_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_PROMOTION_CLOSURE_RECEIPT_BLOCKED"
    )
    assert packet["closure_receipt_ready"] is False
    assert "required_decision_record_completion_receipt_missing" in packet[
        "source_blockers"
    ]
    assert packet["phase1_stabilization_advisory_complete"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_promotion_closure_receipt_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    completion = _read_json(SOURCE_COMPLETION_RECEIPT_PATH)
    completion["promotion_authorized"] = True
    completion["authority_locks"]["promotion"] = True
    source = _write_source(tmp_path, "authorizing_completion.json", completion)

    packet = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(
        REPO_ROOT,
        source_decision_record_completion_receipt_path=source,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_PROMOTION_CLOSURE_RECEIPT_BLOCKED"
    )
    assert "completion_receipt_self_hash_mismatch" in packet["source_blockers"]
    assert (
        "completion_receipt_authority_expanding_field:promotion_authorized"
        in packet["source_blockers"]
    )
    assert "completion_receipt_authority_lock_true:promotion" in packet[
        "source_blockers"
    ]
    assert packet["closure_receipt_ready"] is False
    assert packet["promotion_authorized"] is False


def test_promotion_closure_receipt_unfinalized_source_claim_blocks(
    tmp_path: Path,
) -> None:
    completion = _read_json(SOURCE_COMPLETION_RECEIPT_PATH)
    claim = completion["decision_record_completion_contract"]["completion_claims"][0]
    claim["claim_finalized"] = False
    claim["completion_status"] = "BLOCKED"
    source = _write_source(tmp_path, "unfinalized_completion.json", completion)

    packet = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(
        REPO_ROOT,
        source_decision_record_completion_receipt_path=source,
    )

    assert "completion_receipt_self_hash_mismatch" in packet["source_blockers"]
    assert "completion_contract_claim_not_finalized" in packet["source_blockers"]
    assert packet["closure_receipt_ready"] is False
    assert packet["phase1_stabilization_advisory_complete"] is False


def test_promotion_closure_receipt_contract_shape() -> None:
    packet = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(REPO_ROOT)
    contract = packet["promotion_closure_contract"]
    brier_contract = packet["brier_scoring_contract"]
    rune_mapping = packet["rune_governance_mapping"]

    assert contract["record_id"] == "v2_hygiene_phase1_stabilization_decision_record_001"
    assert contract["record_output_path"] == (
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_001.latest.json"
    )
    assert contract["phase1_stabilization_advisory_complete"] is True
    assert contract["promotion_readiness_classification"] == (
        "ADVISORY_COMPLETE_NOT_CANON_PROMOTED"
    )
    assert contract["closure_claim_count"] == 5
    assert contract["closure_claims_finalized_count"] == 5
    assert all(
        claim["closure_status"] == "CLOSURE_CLAIM_FINALIZED"
        for claim in contract["closure_claims"]
    )
    assert all(
        claim["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
        for claim in contract["closure_claims"]
    )
    assert all(value is False for value in contract["authority_denials"].values())
    assert contract["writeback_performed"] is False
    assert contract["canon_promotion_performed"] is False
    assert contract["runtime_activation_performed"] is False
    assert brier_contract["telemetry_only"] is True
    assert brier_contract["resolution_allowed"] is False
    assert brier_contract["promotion_authorized"] is False
    assert brier_contract["brier_resolution_authorized"] is False
    assert all(
        hook["binary_outcome"] == "NOT_COMPUTABLE"
        for hook in brier_contract["telemetry_hooks"]
    )
    assert {item["rune"] for item in rune_mapping} == {
        "Observe",
        "Bind",
        "Hold",
        "Weigh",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in rune_mapping)


def test_promotion_closure_receipt_preserves_post_closure_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(REPO_ROOT)

    assert packet["decision_record_completed"] is True
    assert packet["decision_record_completion_observed"] is True
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
    assert packet["activation_authorized"] is False
    assert packet["brier_resolution_authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_promotion_closure_receipt_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(REPO_ROOT)
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("closure_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_promotion_closure_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_promotion_closure_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_promotion_closure_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["closure_receipt_hash"] == packet["closure_receipt_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_promotion_closure_receipt_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_stabilization_promotion_closure_receipt_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Promotion Closure Receipt"
    )
    assert any("## Promotion Closure Contract" in line for line in markdown)
    assert any("phase1_stabilization_advisory_complete: True" in line for line in markdown)
    assert any("promotion_authorized: False" in line for line in markdown)
