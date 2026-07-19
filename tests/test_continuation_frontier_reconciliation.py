from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.continuation_frontier_reconciliation import (
    AUTHORITY_LOCKS,
    build_continuation_frontier_reconciliation,
)
from scripts.readiness import run_continuation_frontier_reconciliation

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/continuation_frontier_reconciliation.v1.schema.json"


def _frontier(packet: dict, frontier_id: str) -> dict:
    return next(
        record
        for record in packet["frontier_records"]
        if record["frontier_id"] == frontier_id
    )


def test_continuation_frontier_reconciliation_is_advisory_only() -> None:
    packet = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "ContinuationFrontierReconciliation.v1"
    assert packet["receipt_id"] == "ABRAXAS_CONTINUATION_FRONTIER_RECONCILIATION_001"
    assert packet["receipt_status"] == "CONTINUATION_FRONTIER_RECONCILIATION_EMITTED_ADVISORY_ONLY"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_execution"] is False
    assert packet["authority_drift_observed"] is False
    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["execution_authority"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False


def test_p130_artifact_is_observed_without_canary_regeneration() -> None:
    packet = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)
    p130 = _frontier(packet, "research_canary_p130_final_activation_authorization_review")

    assert p130["classification"] == "OBSERVED"
    assert p130["path_observed"] is True
    assert p130["observed_status"] == "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_RECORD_EMITTED"
    assert packet["p130_artifact_drift"]["code_and_tests_observed"] is True
    assert packet["p130_artifact_drift"]["output_artifact_observed"] is True
    assert packet["p130_artifact_drift"]["classification"] == "OBSERVED"
    assert packet["p130_artifact_drift"]["canary_artifact_regeneration_performed"] is False
    assert packet["research_canary_guardrail"]["do_not_regenerate_research_canary_artifacts"] is True


def test_missing_input_artifacts_are_explicit_not_silent_success(tmp_path: Path) -> None:
    packet = build_continuation_frontier_reconciliation(repo_root=tmp_path)

    assert packet["missing_artifact_records"]
    assert _frontier(packet, "notion_spec_completion_queue")["classification"] == "MISSING_ARTIFACT"
    assert _frontier(packet, "runtime_handoff_receipt_set")["classification"] == "MISSING_ARTIFACT"
    assert packet["classification_counts"]["MISSING_ARTIFACT"] > 0


def test_stale_notion_p131_plus_records_do_not_authorize_implementation() -> None:
    packet = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)

    lanes = {record["lane_id"]: record for record in packet["stale_notion_records"]}
    assert set(lanes) == {
        "P131_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_DECISION_RECORD",
        "P132_RESEARCH_CANARY_FINAL_ACTIVATION_DENIAL_HOLD_ROUTING",
        "P133_RESEARCH_CANARY_LIVE_ACTIVATION_PLAN_DRAFT",
    }
    for lane_id, expected in {
        "P131_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_DECISION_RECORD": True,
        "P132_RESEARCH_CANARY_FINAL_ACTIVATION_DENIAL_HOLD_ROUTING": True,
        "P133_RESEARCH_CANARY_LIVE_ACTIVATION_PLAN_DRAFT": False,
    }.items():
        record = lanes[lane_id]
        assert record["classification"] == "STALE_NOTION_SPEC"
        assert record["repo_authorization_observed"] is expected
    assert packet["research_canary_guardrail"]["p131_plus_implementation_authorized"] is False


def test_registry_repair_chain_completion_is_observed() -> None:
    packet = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)
    record = _frontier(packet, "research_canary_registry_coverage_audit_regeneration_receipt")

    assert record["classification"] == "OBSERVED"
    assert record["path_observed"] is True
    assert record["observed_status"] == "COVERAGE_REPAIR_CHAIN_COMPLETE"
    assert record["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert record["authority_drift_observed"] is False


def test_orphan_policy_chain_closure_is_observed() -> None:
    packet = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)
    record = _frontier(packet, "research_canary_orphan_output_registry_policy_chain_closure_receipt")

    assert record["classification"] == "OBSERVED"
    assert record["path_observed"] is True
    assert record["observed_status"] == "ORPHAN_POLICY_GOVERNANCE_SEALED"
    assert record["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_traceability_audit_regeneration_is_observed() -> None:
    packet = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)
    record = _frontier(packet, "artifact_lineage_traceability_audit_regeneration_receipt")

    assert record["classification"] == "OBSERVED"
    assert record["path_observed"] is True
    assert record["observed_status"] == "TRACEABILITY_AUDIT_REGENERATION_COMPLETE"
    assert record["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_frontier_order_and_hash_are_deterministic() -> None:
    first = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)
    second = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)

    assert first == second
    assert [record["frontier_id"] for record in first["frontier_records"]] == sorted(
        record["frontier_id"] for record in first["frontier_records"]
    )
    packet_without_hash = dict(first)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)


def test_schema_validation() -> None:
    packet = build_continuation_frontier_reconciliation(repo_root=REPO_ROOT)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))

    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/continuation_frontier_reconciliation_001.latest.json"
    out_md = tmp_path / "out/audit/continuation_frontier_reconciliation_001.latest.md"

    first = run_continuation_frontier_reconciliation.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_continuation_frontier_reconciliation.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith("# Continuation Frontier Reconciliation 001\n")
