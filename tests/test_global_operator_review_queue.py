from __future__ import annotations

import json

from core.global_operator_review_queue import (
    build_global_operator_review_queue_artifacts,
    build_queue_item,
    classify_normalized_review_packet,
    normalize_global_ingest_operator_decision_request,
    normalize_scheduler_audit,
    normalize_validation_pack,
    write_global_operator_review_queue_artifacts,
)


def _read(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def test_scheduler_audit_becomes_operator_review_ready():
    packet = normalize_scheduler_audit(_read("out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json"))
    item = build_queue_item(packet)
    assert item["priority"] == "P2"
    assert item["state"] == "eligible_for_operator_review"


def test_clean_shadow_packet_becomes_stabilization_ready():
    packet = normalize_validation_pack(
        _read("out/audit/abx_auto_ingest_validation_pack_001.latest.json"),
        _read("out/projections/aal_viz_ingest_projection_pack_001.latest.json"),
    )
    item = build_queue_item(packet)
    assert item["priority"] == "P2"
    assert item["state"] == "eligible_for_shadow_stabilization"


def test_authority_violation_becomes_p0():
    classified = classify_normalized_review_packet(
        {
            "lane": "GOVERNANCE",
            "authority": {"promotion_allowed": True},
            "negative_proof_complete": True,
            "validation_passed": True,
            "operator_review_ready": True,
        }
    )
    assert classified["priority"] == "P0"
    assert classified["state"] == "rejected"


def test_repo_execution_claim_without_receipt_becomes_p0():
    classified = classify_normalized_review_packet(
        {
            "lane": "GOVERNANCE",
            "authority": {},
            "negative_proof_complete": True,
            "validation_passed": True,
            "operator_review_ready": True,
            "requires_repo_execution_receipt": True,
            "repo_execution_receipt_hash": None,
        }
    )
    assert classified["priority"] == "P0"
    assert classified["state"] == "repo_execution_required"


def test_missing_negative_proof_becomes_p1():
    classified = classify_normalized_review_packet(
        {
            "lane": "SHADOW",
            "authority": {},
            "negative_proof_complete": False,
            "validation_passed": True,
            "operator_review_ready": True,
        }
    )
    assert classified["priority"] == "P1"
    assert classified["state"] == "repair_required"


def test_global_ingest_decision_request_becomes_p0_held_review_item():
    packet = normalize_global_ingest_operator_decision_request(
        _read("out/operator_review/global_ingest_operator_decision_request_001.latest.json")
    )
    item = build_queue_item(packet)
    assert item["priority"] == "P0"
    assert item["state"] == "held"
    assert "prepare_global_ingest_operator_decision_record_template" in item["required_operator_actions"]


def test_queue_run_is_deterministic_and_projection_only(tmp_path):
    artifacts_a = build_global_operator_review_queue_artifacts(".")
    artifacts_b = build_global_operator_review_queue_artifacts(".")
    assert artifacts_a["queue_run"]["run_id"] == artifacts_b["queue_run"]["run_id"]
    assert artifacts_a["queue_run"]["recommended_next_state"] == "review"
    assert artifacts_a["projection_packet"]["projection_only"] is True
    assert artifacts_a["sync_receipt"]["execution_authority"] is False
    assert artifacts_a["queue_run"]["queue_item_count"] == 3
    assert artifacts_a["queue_run"]["p0_count"] == 1
    assert any(item["pipeline_id"] == "oracle_signal" for item in artifacts_a["queue_run"]["items"])

    written = write_global_operator_review_queue_artifacts(tmp_path, source_root=".")
    queue_json = tmp_path / "out/operator_review_queue/latest.json"
    assert queue_json.exists()
    assert written["queue_run"]["queue_item_count"] == 3
