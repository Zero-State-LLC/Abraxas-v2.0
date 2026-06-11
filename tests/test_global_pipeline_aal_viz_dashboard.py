from __future__ import annotations

import json
from pathlib import Path

from core.global_pipeline_aal_viz_dashboard import (
    build_global_pipeline_aal_viz_dashboard_packet,
    build_global_pipeline_aal_viz_view_state,
    write_global_pipeline_aal_viz_dashboard_artifacts,
)


def test_dashboard_packet_is_deterministic_and_projection_only() -> None:
    first = build_global_pipeline_aal_viz_dashboard_packet()
    second = build_global_pipeline_aal_viz_dashboard_packet()

    assert first["dashboard_id"] == second["dashboard_id"]
    assert first["schema_version"] == "GlobalPipelineAALVizDashboardPacket.v1"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["execution_authority"] is False
    assert first["physical_repo_implementation_ready"] is False
    assert first["recommended_next_state"] == "review"
    assert "HOLD_FOR_OPERATOR_REVIEW" in first["recommended_next_commands"]
    assert any(tile["tile_id"] == "authority_lock_panel" and tile["status"] == "LOCKED" for tile in first["tiles"])


def test_dashboard_packet_reflects_doctrine_review_blockers() -> None:
    packet = build_global_pipeline_aal_viz_dashboard_packet()
    assert packet["summary"]["queue_item_count"] == 3
    assert packet["summary"]["held_queue_item_count"] == 1
    assert packet["summary"]["p0_queue_item_count"] == 1
    assert packet["recommended_next_commands"] == [
        "HOLD_FOR_OPERATOR_REVIEW",
        "COLLECT_OPERATOR_DECISION_EVIDENCE",
    ]
    assert "IMPLEMENTATION_AUTHORITY_DENIED" in packet["blocked_reasons"]
    assert "GLOBAL_INGEST_ADAPTER_SPINE_HOLD_ACTIVE" in packet["blocked_reasons"]
    assert "LEGACY_CONTRACT_POSTURE_PRESENT" in packet["blocked_reasons"]
    assert "MISSING_GLOBAL_PIPELINE_CONTRACTS" in packet["blocked_reasons"]
    assert any(panel["panel_id"] == "operator_review_gate" and panel["status"] == "HELD" for panel in packet["panels"])
    assert any(
        panel["panel_id"] == "queue_projection"
        and panel["metrics"]["priority_counts"]["P0"] == 1
        for panel in packet["panels"]
    )
    assert any(alert["alert_id"] == "operator_review_required" and alert["count"] == 1 for alert in packet["alerts"])


def test_view_state_binds_to_dashboard_and_stays_projection_only() -> None:
    packet = build_global_pipeline_aal_viz_dashboard_packet()
    view_state = build_global_pipeline_aal_viz_view_state(packet)

    assert view_state["schema_version"] == "GlobalPipelineAALVizViewState.v1"
    assert view_state["dashboard_id"] == packet["dashboard_id"]
    assert view_state["default_view"] == "overview"
    assert view_state["selected_panel_id"] == "operator_review_gate"
    assert view_state["focus"]["authority_lock_status"] == "LOCKED"
    assert "oracle_signal" in view_state["focus"]["highlighted_pipeline_ids"]
    assert view_state["focus"]["blocked_reason_count"] >= 5


def test_writer_emits_dashboard_and_view_state_artifacts(tmp_path: Path) -> None:
    artifacts = write_global_pipeline_aal_viz_dashboard_artifacts(tmp_path, source_root=".")

    dashboard_path = tmp_path / "out/global_pipeline_aal_viz/dashboard_packet.latest.json"
    view_state_path = tmp_path / "out/global_pipeline_aal_viz/view_state.latest.json"
    assert dashboard_path.exists()
    assert view_state_path.exists()

    dashboard_schema = json.loads(
        Path("contracts/operator_review/global_pipeline_aal_viz_dashboard_packet.v1.schema.json").read_text(encoding="utf-8")
    )
    view_state_schema = json.loads(
        Path("contracts/operator_review/global_pipeline_aal_viz_view_state.v1.schema.json").read_text(encoding="utf-8")
    )
    assert set(dashboard_schema["required"]).issubset(artifacts["dashboard_packet"].keys())
    assert set(view_state_schema["required"]).issubset(artifacts["view_state"].keys())
