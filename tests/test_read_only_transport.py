from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from core.read_only_transport import (
    BLOCKED,
    NOT_COMPUTABLE,
    build_read_only_transport_markdown,
    build_read_only_transport_packet,
    write_read_only_transport_packet,
)
from scripts import run_read_only_transport


def _runtime_projection() -> dict[str, object]:
    return {
        "packet_id": "aal_viz_runtime_projection_001",
        "projection_timestamp": "ts:001",
        "projection_only": True,
        "advisory_only": True,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "inference_authority": False,
        "replay_topology": {"replay_equivalence_status": {"equivalence_verified": True}},
        "remaining_blockers": [],
    }


def _projection_bus() -> dict[str, object]:
    return {
        "packet_id": "projection_bus_001",
        "ledger": {"cursor_bounds": {"first": "cursor:1", "last": "cursor:2"}},
        "advisory_flags": ["projection_only", "advisory_only"],
        "remaining_blockers": [],
        "authority_granted": False,
        "mutation_allowed": False,
    }


def _chronoscope() -> dict[str, object]:
    return {
        "packet_id": "projection_chronoscope_001",
        "playback_cursor_bounds": {"first": "cursor:1", "last": "cursor:2"},
        "lineage_evolution": {"lineage_gap_count": 0},
        "drift_timeline": {"drift_event_count": 0},
        "chronoscope_advisory_flags": ["advisory_only", "deterministic_timeline"],
        "remaining_blockers": [],
        "authority_granted": False,
        "mutation_allowed": False,
    }


def _render_packet() -> dict[str, object]:
    return {
        "packet_id": "aal_viz_graph_render_packet_001",
        "render_advisory_flags": ["advisory_only", "render_only"],
        "remaining_blockers": [],
        "authority_granted": False,
        "mutation_allowed": False,
    }


def _operator_queue() -> dict[str, object]:
    return {
        "queue_id": "operator_action_queue_001",
        "queue_advisory_flags": ["advisory_only", "review_only"],
        "remaining_blockers": [],
        "authority_granted": False,
        "mutation_allowed": False,
    }


def _write_test_artifacts(tmp_path: Path, *, include_refresh: bool = True) -> dict[str, str]:
    payloads = {
        "projection_runtime": _runtime_projection(),
        "projection_bus": _projection_bus(),
        "projection_chronoscope": _chronoscope(),
        "projection_render": _render_packet(),
        "operator_review_queue": _operator_queue(),
        "temporal_state_diff": {
            "temporal_state_diff_status": "ADVISORY_ONLY",
            "total_change_count": 5,
            "topology_change_count": 2,
            "lineage_shift_count": 1,
            "drift_acceleration_status": "DRIFT_ACCELERATING",
            "replay_equivalence_change_status": "SHIFT_DETECTED",
            "queue_delta_count": 3,
            "transport_delta_count": 4,
            "diff_advisory_flags": ["advisory_only", "diff_only", "detection_only"],
        },
    }
    if include_refresh:
        payloads["projection_refresh"] = {
            "packet_id": "live_projection_refresh_001",
            "cursor": "cursor:refresh",
            "authority_granted": False,
            "mutation_allowed": False,
            "remaining_blockers": [],
        }

    paths: dict[str, str] = {}
    for key, payload in payloads.items():
        artifact_path = tmp_path / f"{key}.json"
        artifact_path.write_text(json.dumps(payload), encoding="utf-8")
        paths[key] = str(artifact_path)

    if not include_refresh:
        paths["projection_refresh"] = str(tmp_path / "missing_refresh.json")
    return paths


def test_topic_registry_and_frame_order_stable(tmp_path: Path) -> None:
    paths = _write_test_artifacts(tmp_path)
    packet_a = build_read_only_transport_packet(source_artifact_paths=paths)
    packet_b = build_read_only_transport_packet(source_artifact_paths=paths)

    assert [topic["topic_id"] for topic in packet_a["topics"]] == [
        topic["topic_id"] for topic in packet_b["topics"]
    ]
    assert [frame["frame_id"] for frame in packet_a["frames"]] == [
        frame["frame_id"] for frame in packet_b["frames"]
    ]
    assert packet_a["ledger"]["ledger_hash"] == packet_b["ledger"]["ledger_hash"]
    assert packet_a["ledger"]["ordered_topics"] == [
        topic["topic_id"] for topic in packet_a["topics"]
    ]


def test_cursor_bounds_and_invariants_locked(tmp_path: Path) -> None:
    packet = build_read_only_transport_packet(
        source_artifact_paths=_write_test_artifacts(tmp_path)
    )
    assert packet["transport_cursor_bounds"]["first"] is not None
    assert packet["transport_cursor_bounds"]["last"] is not None
    assert packet["read_only"] is True
    assert packet["advisory_only"] is True
    assert packet["transport_only"] is True
    assert packet["command_channel"] is False
    assert packet["bidirectional_control"] is False
    assert packet["execution_authority"] is False
    assert packet["mutation_allowed"] is False
    assert packet["auto_execute"] is False
    assert packet["auto_approve"] is False
    assert packet["temporal_state_diff_status"] == "ADVISORY_ONLY"
    assert packet["total_change_count"] == 5
    assert packet["topology_change_count"] == 2
    assert packet["lineage_shift_count"] == 1
    assert packet["queue_delta_count"] == 3
    assert packet["transport_delta_count"] == 4
    assert packet["temporal_stability_pressure_status"] == NOT_COMPUTABLE
    assert packet["aggregate_stress_score"] == 0.0
    assert packet["pressure_zone_count"] == 0


def test_missing_artifact_fail_closed_not_computable_frame(tmp_path: Path) -> None:
    packet = build_read_only_transport_packet(
        source_artifact_paths=_write_test_artifacts(tmp_path, include_refresh=False)
    )
    refresh_frame = next(
        frame for frame in packet["frames"] if frame["topic_name"] == "projection.refresh"
    )
    assert refresh_frame["blocker_status"] == NOT_COMPUTABLE
    assert "missing_artifact:" in " ".join(refresh_frame["remaining_blockers"])
    assert packet["final_status"] in {NOT_COMPUTABLE, BLOCKED, "ADVISORY_ONLY"}


def test_authority_boundary_violation_blocks_frame(tmp_path: Path) -> None:
    paths = _write_test_artifacts(tmp_path)
    runtime_path = Path(paths["projection_runtime"])
    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    payload["authority_granted"] = True
    runtime_path.write_text(json.dumps(payload), encoding="utf-8")

    packet = build_read_only_transport_packet(source_artifact_paths=paths)
    runtime_frame = next(
        frame for frame in packet["frames"] if frame["topic_name"] == "projection.runtime"
    )
    assert runtime_frame["blocker_status"] == BLOCKED
    assert any(
        isinstance(item, str) and item.startswith("authority_boundary_violation:")
        for item in runtime_frame["remaining_blockers"]
    )
    assert packet["final_status"] == BLOCKED


def test_writer_markdown_and_run_script(tmp_path: Path) -> None:
    paths = _write_test_artifacts(tmp_path)
    packet = build_read_only_transport_packet(source_artifact_paths=paths)
    out_path = tmp_path / "read_only_transport.json"
    write_read_only_transport_packet(out_path, packet)
    markdown = build_read_only_transport_markdown(packet)

    assert out_path.read_text(encoding="utf-8").endswith("\n")
    assert "Read-Only Transport" in markdown
    assert "read_only" in markdown

    source_map = {
        "out/projections/aal_viz_runtime_projection_001.latest.json": _runtime_projection(),
        "out/projections/live_projection_refresh_001.latest.json": {
            "packet_id": "live_projection_refresh_001",
            "cursor": "cursor:refresh",
            "authority_granted": False,
            "mutation_allowed": False,
            "remaining_blockers": [],
        },
        "out/projections/projection_bus_001.latest.json": _projection_bus(),
        "out/projections/projection_chronoscope_001.latest.json": _chronoscope(),
        "out/projections/aal_viz_graph_render_packet_001.latest.json": _render_packet(),
        "out/audit/operator_action_queue_001.latest.json": _operator_queue(),
        "out/projections/temporal_state_diff_001.latest.json": {
            "temporal_state_diff_status": "ADVISORY_ONLY",
            "total_change_count": 0,
            "topology_change_count": 0,
            "lineage_shift_count": 0,
            "drift_acceleration_status": "NO_ACCELERATION",
            "replay_equivalence_change_status": "NO_CHANGE",
            "queue_delta_count": 0,
            "transport_delta_count": 0,
            "diff_advisory_flags": ["advisory_only", "diff_only", "detection_only"],
        },
    }

    def _mock_load(path: str | Path | None) -> dict[str, object] | None:
        return source_map.get(str(path))

    runtime_paths = run_read_only_transport.RuntimePaths(
        contracts_dir=tmp_path / "contracts", out_dir=tmp_path / "out"
    )
    with (
        patch("core.read_only_transport._load_artifact", side_effect=_mock_load),
        patch.object(run_read_only_transport, "_PATHS", runtime_paths),
        patch.object(run_read_only_transport, "OUT_PATH", runtime_paths.read_only_transport_latest),
    ):
        run_read_only_transport.main()

    assert runtime_paths.read_only_transport_latest.exists()
    assert runtime_paths.read_only_transport_latest.with_suffix(".md").exists()
