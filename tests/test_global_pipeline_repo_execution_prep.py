from __future__ import annotations

from pathlib import Path

from core.global_pipeline_repo_execution_prep import (
    build_global_pipeline_repo_execution_prep_packet,
    write_global_pipeline_repo_execution_prep_artifacts,
)


def test_prep_packet_stays_projection_only() -> None:
    packet = build_global_pipeline_repo_execution_prep_packet()
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["promotion_allowed"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["execution_authority"] is False


def test_prep_packet_remains_fail_closed_until_operator_review_is_cleared() -> None:
    packet = build_global_pipeline_repo_execution_prep_packet()
    assert packet["physical_repo_implementation_ready"] is False
    assert packet["status"] == "REPO_EXECUTION_PREP_PACKET_BLOCKED"
    assert packet["recommended_next_state"] == "hold"
    assert packet["queue_summary"]["queue_item_count"] == 3
    assert packet["queue_summary"]["state_counts"]["review_completed"] == 3
    assert "out/global_pipeline_registry/latest.json" not in packet["missing_dependency_paths"]
    assert (
        "out/global_pipeline_doctrine_validation/latest.json"
        not in packet["missing_dependency_paths"]
    )
    assert (
        "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json"
        not in packet["missing_dependency_paths"]
    )
    assert "out/global_pipeline_aal_viz/dashboard_packet.latest.json" not in packet["missing_dependency_paths"]
    assert "out/global_pipeline_aal_viz/view_state.latest.json" not in packet["missing_dependency_paths"]
    assert "MISSING_GLOBAL_PIPELINE_SPINE_SURFACES" not in packet["not_computable_reasons"]
    assert "GLOBAL_PIPELINE_OPERATOR_REVIEW_REQUIRED" in packet["not_computable_reasons"]
    assert packet["recommended_next_commands"] == [
        "HOLD_FOR_OPERATOR_REVIEW",
        "REQUEST_GLOBAL_PIPELINE_REPAIR",
    ]


def test_prep_writer_emits_spec_only_receipt_and_packet(tmp_path: Path) -> None:
    artifacts = write_global_pipeline_repo_execution_prep_artifacts(tmp_path, source_root=".")
    packet = artifacts["prep_packet"]
    receipt = artifacts["repo_execution_receipt"]

    assert packet["command"] == "RUN_GLOBAL_PIPELINE_REPO_EXECUTION_PREP_001"
    assert receipt["command_id"] == "RUN_GLOBAL_PIPELINE_REPO_EXECUTION_PREP_001"
    assert receipt["execution_state"] == "not_executed"
    assert receipt["status"] == "spec_only"

    assert (tmp_path / "out/operator_review/global_pipeline_repo_execution_prep_001.latest.json").exists()
    assert (tmp_path / "out/execution_receipts/global_pipeline_repo_prep.latest.json").exists()
