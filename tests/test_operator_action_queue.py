from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from core.config import RuntimePaths
from core.operator_action_queue import (
    NOT_COMPUTABLE,
    build_operator_action_queue_markdown,
    build_operator_action_queue_packet,
    summarize_operator_action_queue,
    write_operator_action_queue_packet,
)
from scripts import run_operator_action_queue


def _runtime_profile() -> dict[str, object]:
    return {
        "patch_id": "PATCH-P8-RUNTIME-PERFORMANCE-PROFILING-001",
        "final_status": "PASS",
        "profile_enabled": True,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _runtime_benchmark(*, regression: bool = True) -> dict[str, object]:
    delta_ns = 250_000 if regression else -250_000
    delta_pct = 12.5 if regression else -12.5
    return {
        "schema": "RuntimeBenchmarkArtifact.v1",
        "artifact_id": "runtime_benchmark_001",
        "patch_id": "PATCH-P10-RUNTIME-BENCHMARK-AND-DRIFT-GUARD-001",
        "drift_report": {
            "drift_detected": True,
            "detections": ["variance_spike", "output_hash_drift"],
            "performance_delta": {
                "delta_ns": delta_ns,
                "delta_pct": delta_pct,
                "baseline_mean_ns": 2_000_000,
                "optimized_mean_ns": 2_250_000,
            },
            "report_hash": "benchmark-report-hash",
            "advisory": {
                "output_hash_drift": True,
                "replay_divergence_detected": True,
                "cache_contamination_detected": False,
                "variance_spike_detected": True,
                "serialization_instability_detected": False,
                "artifact_ordering_drift_detected": False,
            },
        },
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _stabilization() -> dict[str, object]:
    return {
        "stabilization_arc": {"patch_id": "PATCH-P6-STABILIZATION-RELEASE-READINESS-001"},
        "release_readiness": {"status": "ready_for_manual_release_review"},
        "final_posture": {
            "status": "STABILIZED_RELEASE_READINESS_RECORDED",
            "authority_granted": False,
            "mutation_allowed": False,
            "promotion_allowed": False,
        },
    }


def _governance_freeze() -> dict[str, object]:
    return {
        "patch_id": "PATCH-P7-MANUAL-RELEASE-TAG-AND-GOVERNANCE-FREEZE-001",
        "freeze_status": "FROZEN",
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _incremental_replay(*, equivalence_verified: bool = False) -> dict[str, object]:
    return {
        "schema": "IncrementalReplayPlan.v1",
        "patch_id": "PATCH-P12-REPLAY-SCALING-AND-INCREMENTAL-EXECUTION-001",
        "final_status": "ADVISORY_ONLY",
        "replay_equivalence_verified": equivalence_verified,
        "remaining_blockers": ["replay_equivalence_not_held"],
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _operator_console() -> dict[str, object]:
    return {
        "packet_id": "operator_runtime_console_001",
        "final_status": "BLOCKED",
        "operator_next_actions": [
            "BLOCKED: Generate missing source artifact — out/audit/runtime_performance_profile_001.latest.json"
        ],
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "projection_only": True,
        "advisory_only": True,
    }


def _projection_bus() -> dict[str, object]:
    return {
        "schema": "ProjectionBusEnvelope.v1",
        "final_status": "BLOCKED",
        "remaining_blockers": ["missing_indexable_snapshots"],
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _runtime_projection(*, blocked: bool = True) -> dict[str, object]:
    return {
        "schema": "RuntimeProjectionPacket.v1",
        "projection_id": "projection-1",
        "final_status": "BLOCKED" if blocked else "PASS",
        "remaining_blockers": ["operator_blocker:missing_artifact:runtime_profile"] if blocked else [],
        "replay_topology": {
            "replay_equivalence_status": {
                "equivalence_verified": False,
                "final_status": "BLOCKED",
            }
        },
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "projection_only": True,
        "advisory_only": True,
    }


def _chronoscope() -> dict[str, object]:
    return {
        "schema": "ProjectionChronoscopePacket.v1",
        "packet_hash": "chronoscope-hash",
        "final_status": "BLOCKED",
        "remaining_blockers": ["corrupt_lineage:lineage_prev_missing:s2->missing"],
        "lineage_evolution": {
            "lineage_gap_count": 2,
            "corrupt_lineage_count": 1,
        },
        "drift_timeline": {
            "drift_events": ["variance_spike"],
        },
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _graph_render_packet() -> dict[str, object]:
    return {
        "schema": "AALVizGraphRenderPacket.v1",
        "packet_hash": "render-hash",
        "final_status": "BLOCKED",
        "remaining_blockers": ["blocked_layer:chronoscope_timeline_layer"],
        "render_blocker_count": 1,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "render_only": True,
        "advisory_only": True,
        "projection_only": True,
    }


def _temporal_state_diff() -> dict[str, object]:
    return {
        "schema": "TemporalStateDiff.v1",
        "temporal_state_diff_status": "ADVISORY_ONLY",
        "total_change_count": 7,
        "topology_change_count": 2,
        "lineage_shift_count": 1,
        "drift_acceleration_status": "DRIFT_ACCELERATING",
        "replay_equivalence_change_status": "SHIFT_DETECTED",
        "queue_delta_count": 3,
        "transport_delta_count": 4,
        "diff_advisory_flags": ["advisory_only", "diff_only", "detection_only"],
    }


def _artifact_payloads() -> dict[str, dict[str, object]]:
    return {
        "runtime_performance_profile": _runtime_profile(),
        "runtime_benchmark": _runtime_benchmark(),
        "stabilization_release_readiness": _stabilization(),
        "governance_freeze_baseline": _governance_freeze(),
        "incremental_replay": _incremental_replay(),
        "operator_console": _operator_console(),
        "projection_bus": _projection_bus(),
        "runtime_projection": _runtime_projection(),
        "projection_chronoscope": _chronoscope(),
        "graph_render_packet": _graph_render_packet(),
        "temporal_state_diff": _temporal_state_diff(),
    }


def _write_payloads(tmp_path: Path, *, include_missing: bool = False) -> dict[str, str]:
    paths: dict[str, str] = {}
    for key, payload in _artifact_payloads().items():
        file_path = tmp_path / f"{key}.json"
        file_path.write_text(json.dumps(payload), encoding="utf-8")
        paths[key] = str(file_path)
    if include_missing:
        paths["runtime_performance_profile"] = str(tmp_path / "missing-runtime-profile.json")
        paths["graph_render_packet"] = str(tmp_path / "missing-render.json")
    return paths


def test_queue_item_ordering_and_hash_are_stable(tmp_path: Path) -> None:
    paths = _write_payloads(tmp_path)
    packet_a = build_operator_action_queue_packet(source_artifact_paths=paths)
    packet_b = build_operator_action_queue_packet(source_artifact_paths=paths)

    def sort_key(item: dict[str, object]) -> tuple[int, object, object, object]:
        return (
            {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[str(item["severity"])],
            item["category"],
            item["source_artifact"],
            item["item_id"],
        )

    assert [item["item_id"] for item in packet_a["operator_action_items"]] == [
        item["item_id"] for item in packet_b["operator_action_items"]
    ]
    assert packet_a["queue_hash"] == packet_b["queue_hash"]
    assert packet_a["severity_counts"] == packet_b["severity_counts"]
    assert packet_a["operator_action_items"] == sorted(
        packet_a["operator_action_items"], key=sort_key
    )


def test_missing_sources_fail_closed_with_review_items(tmp_path: Path) -> None:
    paths = _write_payloads(tmp_path, include_missing=True)
    packet = build_operator_action_queue_packet(source_artifact_paths=paths)

    missing_items = [
        item
        for item in packet["operator_action_items"]
        if item["category"] == "missing_artifact_review"
    ]
    assert len(missing_items) == 4
    assert packet["final_status"] == "ADVISORY_ONLY"
    assert all(item["source_artifact"] in packet["blocked_sources"] for item in missing_items)


def test_blocked_and_corrupt_surfaces_create_expected_reviews_and_escalations(tmp_path: Path) -> None:
    paths = _write_payloads(tmp_path)
    packet = build_operator_action_queue_packet(source_artifact_paths=paths)

    categories = {item["category"] for item in packet["operator_action_items"]}
    assert "blocked_projection_review" in categories
    assert "lineage_gap_review" in categories
    assert "replay_equivalence_review" in categories
    assert "render_blocker_review" in categories

    reason_codes = {item["reason_code"] for item in packet["escalation_paths"]}
    assert "repeated_blocked_status" in reason_codes
    assert "corrupt_lineage" in reason_codes
    assert "failed_replay_equivalence" in reason_codes
    assert "drift_above_threshold" in reason_codes


def test_checkpoints_and_invariants_are_locked(tmp_path: Path) -> None:
    paths = _write_payloads(tmp_path)
    packet = build_operator_action_queue_packet(source_artifact_paths=paths)

    assert packet["execution_authority"] is False
    assert packet["authority_granted"] is False
    assert packet["mutation_allowed"] is False
    assert packet["promotion_allowed"] is False
    assert packet["auto_execute"] is False
    assert packet["auto_approve"] is False

    assert packet["approval_checkpoints"]
    checkpoint = packet["approval_checkpoints"][0]
    assert checkpoint["decision_status"] == "PENDING"
    assert checkpoint["execution_unlocked"] is False
    assert checkpoint["auto_execute"] is False
    assert checkpoint["auto_approve"] is False

    for item in packet["operator_action_items"] + packet["approval_checkpoints"] + packet["escalation_paths"] + packet["action_lineage_receipts"]:
        assert item["authority_granted"] is False
        assert item["mutation_allowed"] is False
        assert item["promotion_allowed"] is False
        assert item["execution_authority"] is False
        assert item["auto_execute"] is False
        assert item["auto_approve"] is False


def test_build_does_not_mutate_source_artifacts(tmp_path: Path) -> None:
    paths = _write_payloads(tmp_path)
    before = {key: Path(path).read_text(encoding="utf-8") for key, path in paths.items()}

    build_operator_action_queue_packet(source_artifact_paths=paths)

    after = {key: Path(path).read_text(encoding="utf-8") for key, path in paths.items()}
    assert before == after


def test_summary_writer_and_markdown(tmp_path: Path) -> None:
    paths = _write_payloads(tmp_path)
    packet = build_operator_action_queue_packet(source_artifact_paths=paths)
    out_path = tmp_path / "operator_action_queue.json"

    written = write_operator_action_queue_packet(out_path, packet)
    markdown = build_operator_action_queue_markdown(packet)
    summary = summarize_operator_action_queue(packet)

    assert written == out_path
    assert out_path.read_text(encoding="utf-8").endswith("\n")
    assert "Operator Action Queue" in markdown
    assert summary["operator_action_queue_status"] == packet["final_status"]
    assert summary["operator_action_item_count"] == packet["operator_action_item_count"]
    assert summary["temporal_state_diff_status"] == "ADVISORY_ONLY"
    assert summary["total_change_count"] == 7
    assert summary["topology_change_count"] == 2
    assert summary["lineage_shift_count"] == 1
    assert summary["queue_delta_count"] == 3
    assert summary["transport_delta_count"] == 4
    assert summary["temporal_topology_cartography_status"] == NOT_COMPUTABLE
    assert summary["atlas_region_count"] == 0
    assert summary["atlas_corridor_count"] == 0
    assert summary["topology_density_score"] == 0.0
    assert summary["temporal_stability_pressure_status"] == NOT_COMPUTABLE
    assert summary["aggregate_stress_score"] == 0.0
    assert summary["pressure_zone_count"] == 0
    assert summarize_operator_action_queue(None)["operator_action_queue_status"] == NOT_COMPUTABLE


def test_run_script_writes_queue_artifacts(tmp_path: Path) -> None:
    runtime_paths = RuntimePaths(contracts_dir=tmp_path / "contracts", out_dir=tmp_path / "out")
    source_paths = {
        runtime_paths.runtime_performance_profile_latest: _runtime_profile(),
        runtime_paths.runtime_benchmark_latest: _runtime_benchmark(),
        runtime_paths.stabilization_release_readiness_latest: _stabilization(),
        runtime_paths.governance_freeze_baseline_latest: _governance_freeze(),
        runtime_paths.incremental_replay_latest: _incremental_replay(),
        runtime_paths.operator_runtime_console_latest: _operator_console(),
        runtime_paths.projection_bus_latest: _projection_bus(),
        runtime_paths.aal_viz_runtime_projection_latest: _runtime_projection(),
        runtime_paths.projection_chronoscope_latest: _chronoscope(),
        runtime_paths.aal_viz_graph_render_packet_latest: _graph_render_packet(),
        runtime_paths.temporal_state_diff_latest: _temporal_state_diff(),
    }
    for path, payload in source_paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    out_path = runtime_paths.operator_action_queue_latest
    with (
        patch.object(run_operator_action_queue, "_PATHS", runtime_paths),
        patch.object(run_operator_action_queue, "OUT_PATH", out_path),
    ):
        run_operator_action_queue.main()

    assert out_path.exists()
    assert out_path.with_suffix(".md").exists()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema"] == "OperatorReviewQueue.v1"
    assert payload["operator_action_queue_status"] == "ADVISORY_ONLY"
